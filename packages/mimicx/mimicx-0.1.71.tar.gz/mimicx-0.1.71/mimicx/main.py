import os
import platform
import re
import base64
from pathlib import Path
from typing import Union, Any
import numpy as np
import importlib
from pathlib import Path
import urllib.request
import asyncio
import sys
import json

# Detect if running in Pyodide environment
IS_PYODIDE = "pyodide" in sys.modules or hasattr(sys, "_getframe") and "pyodide" in str(sys._getframe())

# Import pyodide-specific modules only if in Pyodide environment
if IS_PYODIDE:
    try:
        import js
        import pyodide
        from pyodide.http import pyfetch
        print("Running in Pyodide environment - Python support enabled")
    except ImportError:
        print("Pyodide detected but imports failed")
        IS_PYODIDE = False

class APIClient:
    """API client for handling method calls in Pyodide environment"""
    
    def __init__(self, base_url: str, api_version: str, enterpriseId: str, module: str, algorithm: str):
        self.base_url = base_url.rstrip('/')
        self.api_version = api_version
        self.enterpriseId = enterpriseId
        self.module = module
        self.algorithm = algorithm
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    async def call_api(self, method_name: str, *args, **kwargs):
        """Make API call for the given method"""
        # Construct API endpoint
        endpoint = f"{self.base_url}/api/{self.api_version}/{self.enterpriseId}/{self.module}/{self.algorithm}/{method_name}"
        
        # Prepare request data
        request_data = {
            'args': self._serialize_args(args),
            'kwargs': self._serialize_kwargs(kwargs),
            'method': method_name
        }
        
        try:
            if IS_PYODIDE:
                # Use pyfetch for Pyodide environment
                response = await pyfetch(
                    endpoint,
                    method='POST',
                    headers=self.headers,
                    body=json.dumps(request_data)
                )
                
                if response.status == 200:
                    result = await response.json()
                    return self._deserialize_result(result)
                else:
                    error_text = await response.text()
                    raise Exception(f"API call failed with status {response.status}: {error_text}")
            else:
                # Fallback for non-Pyodide environments (shouldn't happen in this context)
                import requests
                response = requests.post(endpoint, json=request_data, headers=self.headers)
                response.raise_for_status()
                return self._deserialize_result(response.json())
                
        except Exception as e:
            print(f"API call failed for {method_name}: {e}")
            raise
    
    def _serialize_args(self, args):
        """Serialize arguments for API transmission"""
        serialized = []
        for arg in args:
            if isinstance(arg, np.ndarray):
                # Convert numpy arrays to lists
                serialized.append({
                    'type': 'numpy_array',
                    'data': arg.tolist(),
                    'dtype': str(arg.dtype),
                    'shape': arg.shape
                })
            elif hasattr(arg, '__dict__'):
                # Handle custom objects
                serialized.append({
                    'type': 'object',
                    'class': arg.__class__.__name__,
                    'data': arg.__dict__
                })
            else:
                # Basic types
                serialized.append({
                    'type': 'basic',
                    'data': arg
                })
        return serialized
    
    def _serialize_kwargs(self, kwargs):
        """Serialize keyword arguments for API transmission"""
        serialized = {}
        for key, value in kwargs.items():
            if isinstance(value, np.ndarray):
                serialized[key] = {
                    'type': 'numpy_array',
                    'data': value.tolist(),
                    'dtype': str(value.dtype),
                    'shape': value.shape
                }
            elif hasattr(value, '__dict__'):
                serialized[key] = {
                    'type': 'object',
                    'class': value.__class__.__name__,
                    'data': value.__dict__
                }
            else:
                serialized[key] = {
                    'type': 'basic',
                    'data': value
                }
        return serialized
    
    def _deserialize_result(self, result):
        """Deserialize API response"""
        if isinstance(result, dict):
            if result.get('type') == 'numpy_array':
                # Reconstruct numpy array
                return np.array(result['data'], dtype=result['dtype']).reshape(result['shape'])
            elif result.get('type') == 'error':
                # Handle API errors
                raise Exception(result.get('message', 'Unknown API error'))
            elif 'data' in result:
                return result['data']
        
        return result

class Model:

    def __init__(self, domainAlgorithm):
        self.modelFolderUrl = 'https://speedpresta.s3.us-east-1.amazonaws.com/mimicx'
        self.modelNameBase = 'mimicx_'
        
        # API configuration for Pyodide environment
        self.api_base_url = 'https://api.mimicx.ai'  # Configure your API server URL
        self.api_version = 'v1'
        self.enterpriseId = 'MIMICX-PIP'
        
        parts = domainAlgorithm.split('/')
        if len(parts) == 2:
            self.module, self.algorithm = parts
        else:
            # Handle the error gracefully
            raise ValueError(f"Invalid format for domainAlgorithm: '{domainAlgorithm}'. Expected format 'module/algorithm'.")

        self.module, self.algorithm = (domainAlgorithm.split('/'))
        self.module_dir = os.path.dirname(__file__)
        self.algorithms_directory = self.module_dir
        self.model = None
        self.dataType = None
        self.model_loaded = False
        
        # Initialize API client for Pyodide environment
        if IS_PYODIDE:
            self.api_client = APIClient(self.api_base_url, self.api_version, self.enterpriseId, self.module, self.algorithm)
            print(f"Initialized API client for Pyodide environment: {self.module}/{self.algorithm}")
        else:
            self.api_client = None
            # Try to load the model during initialization for non-Pyodide
            try:
                self.load_model_file_sync(self.algorithm)
                if self.model is not None:
                    self.model_loaded = True
            except Exception as e:
                print(f"Warning: Could not load model during initialization: {e}")

    def get_model(self):
        return self.model

    def set_model(self, algorithm):
        # In Pyodide, we don't actually load models locally
        if IS_PYODIDE:
            print(f"Pyodide environment: Model '{algorithm}' will be handled via API calls")
            self.model_loaded = True
            return True
            
        # Original model loading logic for non-Pyodide environments
        if algorithm:
            module_name = f"mimicx_{algorithm}"
            class_name = f"Mimicx{algorithm.replace('_', ' ').title().replace(' ', '')}"
            
            print(f"Attempting to import module: {module_name}")
            print(f"Looking for class: {class_name}")

            try:
                # Try relative import first
                print("Trying relative import...")
                module = importlib.import_module(f".{module_name}", package=__package__)
                print(f"Relative import successful for {module_name}")
            except ImportError as e:
                print(f"Relative import failed: {e}")
                try:
                    # Try absolute import
                    print("Trying absolute import...")
                    module = importlib.import_module(module_name)
                    print(f"Absolute import successful for {module_name}")
                except ImportError as e:
                    print(f"Failed to import module '{module_name}': {e}")
                    print(f"Available modules in sys.modules containing 'mimicx': {[m for m in sys.modules.keys() if 'mimicx' in m]}")
                    return False

            try:
                print(f"Module imported successfully. Module contents: {dir(module)}")
                model_class = getattr(module, class_name)
                print(f"Found class {class_name} in module")
                self.model = model_class()
                print(f"Successfully instantiated model: {class_name}")
                return True
            except AttributeError as e:
                print(f"Class '{class_name}' not found in module '{module_name}'. Available classes: {[name for name in dir(module) if not name.startswith('_')]}")
                print(f"AttributeError: {e}")
                return False
            except Exception as e:
                print(f"Error instantiating class '{class_name}': {e}")
                print(f"Exception type: {type(e)}")
                return False
        else:
            print("No algorithm provided to set_model")
            return False

    def __getattr__(self, attr):
        # In Pyodide environment, redirect all method calls to API
        if IS_PYODIDE and self.api_client:
            print(f"Pyodide: Redirecting method '{attr}' to API call")
            
            def sync_api_method(*args, **kwargs):
                """Synchronous wrapper for API calls in Pyodide"""
                try:
                    # Use Pyodide's built-in mechanism to handle async calls synchronously
                    import asyncio
                    
                    # Get or create event loop
                    try:
                        loop = asyncio.get_running_loop()
                        # If there's a running loop, we need to use a different approach
                        if loop.is_running():
                            # In Pyodide, we can use the js module to handle this
                            try:
                                import js
                                # Use Pyodide's await mechanism
                                coro = self.api_client.call_api(attr, *args, **kwargs)
                                # Convert coroutine to Promise and wait for it
                                from pyodide.ffi import to_js
                                from js import Promise
                                
                                # Create a synchronous-looking call using Pyodide's capabilities
                                import asyncio
                                import concurrent.futures
                                
                                # Use a simple approach: create a new task and get result
                                future = asyncio.ensure_future(coro)
                                
                                # For Pyodide, we'll use a different approach
                                # Since we can't easily block in browser environment,
                                # we'll use a synchronous XMLHttpRequest instead
                                return self._sync_api_call(attr, *args, **kwargs)
                                
                            except Exception as e:
                                print(f"Pyodide sync call failed: {e}")
                                return self._sync_api_call(attr, *args, **kwargs)
                        else:
                            # No running loop, can use asyncio.run
                            return asyncio.run(self.api_client.call_api(attr, *args, **kwargs))
                    except RuntimeError:
                        # No event loop exists, create one
                        return asyncio.run(self.api_client.call_api(attr, *args, **kwargs))
                        
                except Exception as e:
                    print(f"Sync API call failed: {e}")
                    # Fallback to sync HTTP request
                    return self._sync_api_call(attr, *args, **kwargs)
            
            return sync_api_method
        
        # Original logic for non-Pyodide environments
        # Check if model is loaded, if not try to load it
        if self.model is None and not self.model_loaded:
            print(f"Model not loaded, attempting to load algorithm: {self.algorithm}")
            
            try:
                # Try sync loading first
                success = self.load_model_file_sync(self.algorithm)
                print(f"load_model_file_sync returned: {success}")
                
                if success and self.model is not None:
                    self.model_loaded = True
                    print("Model loaded successfully")
                elif success and self.model is None:
                    # Loading succeeded but model is still None - try direct setting
                    print("Loading succeeded but model is None, trying direct set_model")
                    direct_success = self.set_model(self.algorithm)
                    print(f"Direct set_model returned: {direct_success}")
                    if direct_success and self.model is not None:
                        self.model_loaded = True
                        print("Model loaded successfully via direct setting")
                    else:
                        print(f"Direct setting failed. Model is: {self.model}")
                        raise AttributeError(f"Model '{self.algorithm}' files were found/downloaded but could not be imported. "
                                           f"Check the module structure and naming.")
                else:
                    # Loading failed completely
                    print(f"Loading failed completely. Success: {success}, Model: {self.model}")
                    raise AttributeError(f"Model '{self.algorithm}' could not be loaded. "
                                       f"Check that the model exists and is accessible.")
                        
            except Exception as e:
                print(f"Exception during model loading: {str(e)}")
                raise AttributeError(f"Could not load model and attribute '{attr}' not found. Error: {e}")
        
        # If model is still None after loading attempt, raise clear error
        if self.model is None:
            raise AttributeError(f"Failed to load model '{self.algorithm}' for attribute '{attr}'. "
                               f"Model loading returned False, direct setting returned False, model is None")
        
        # Check if the attribute exists on the model
        if hasattr(self.model, attr):
            return getattr(self.model, attr)
        else:
            raise AttributeError(f"'{type(self.model).__name__}' object has no attribute '{attr}'")

    def _sync_api_call(self, method_name: str, *args, **kwargs):
        """Make synchronous API call using XMLHttpRequest in Pyodide"""
        try:
            import js
            import json
            from pyodide.ffi import to_js
            
            # Construct API endpoint
            endpoint = f"{self.api_base_url}/api/{self.api_version}/{self.enterpriseId}/{self.module}/{self.algorithm}/{method_name}"
            
            # Prepare request data
            request_data = {
                'args': self.api_client._serialize_args(args),
                'kwargs': self.api_client._serialize_kwargs(kwargs),
                'method': method_name
            }
            
            # Use JavaScript to make synchronous request
            js_code = f"""
            (function() {{
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '{endpoint}', false);
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.setRequestHeader('Accept', 'application/json');
                xhr.send('{json.dumps(request_data)}');
                
                if (xhr.status === 200) {{
                    return JSON.parse(xhr.responseText);
                }} else {{
                    throw new Error('API call failed with status ' + xhr.status + ': ' + xhr.responseText);
                }}
            }})()
            """
            
            # Execute JavaScript code synchronously
            result = js.eval(js_code)
            
            # Convert JavaScript object to Python and deserialize
            python_result = result.to_py()
            return self.api_client._deserialize_result(python_result)
                
        except Exception as e:
            print(f"Sync API call failed: {e}")
            # Return a meaningful error message
            return f"API Error: Could not execute {method_name}. {str(e)}"

    # Enhanced async method support for Pyodide
    async def call_async(self, method_name: str, *args, **kwargs):
        """Explicitly call a method asynchronously in Pyodide environment"""
        if IS_PYODIDE and self.api_client:
            return await self.api_client.call_api(method_name, *args, **kwargs)
        else:
            # For non-Pyodide, call the local method if it exists
            if hasattr(self.model, method_name):
                method = getattr(self.model, method_name)
                if asyncio.iscoroutinefunction(method):
                    return await method(*args, **kwargs)
                else:
                    return method(*args, **kwargs)
            else:
                raise AttributeError(f"Method '{method_name}' not found")

    def get_platform_extensions(self):
        """Get appropriate file extensions based on the current platform"""
        if IS_PYODIDE:
            # In Pyodide, only use Python files
            return ['.cpython-312-wasm32-emscripten.wasm', '.py']
        elif platform.system() == "Windows":
            return ['.cp39-win_amd64.pyd', '.py']
        elif platform.system() == "Darwin":
            return ['.cpython-39-darwin.so', '.py']
        else:
            return ['.cpython-311-x86_64-linux-gnu.so', '.py']

    async def load_model_file(self, model):
        """Async version for downloading files - skipped in Pyodide API mode"""
        if IS_PYODIDE:
            print("Pyodide environment: Model loading skipped, using API calls")
            return True
            
        # Original async loading logic for non-Pyodide environments
        # Check and Create Algorithms Directory
        if not os.path.exists(self.algorithms_directory):
            os.makedirs(self.algorithms_directory)

        extensions = self.get_platform_extensions()
        print(f"Platform detected: {'Pyodide' if IS_PYODIDE else platform.system()}")
        print(f"Trying extensions: {extensions}")
        
        for extension in extensions:
            file_path = os.path.join(self.algorithms_directory, self.modelNameBase + model + extension)
            
            if os.path.exists(file_path):
                print(f"Found existing model file: {file_path}")
                success = self.set_model(model)
                if success:
                    return True
            else:
                try:
                    url = self.modelFolderUrl + '/' + self.module + '/' + model + '/' + self.modelNameBase + model + extension
                    print(f"Attempting to download model from: {url}")

                    # Use urllib for non-Pyodide environments
                    urllib.request.urlretrieve(url, file_path)
                    print(f"Successfully downloaded model to: {file_path}")
                    
                    success = self.set_model(model)
                    if success:
                        return True
                except Exception as e:
                    print(f"Failed to download {extension} version: {e}")
                    if os.path.exists(file_path):
                        os.remove(file_path)  # Clean up partial download
                    continue
        
        return False

    def load_model_file_sync(self, model):
        """Synchronous version - skipped in Pyodide API mode"""
        if IS_PYODIDE:
            print("Pyodide environment: Model loading skipped, using API calls")
            return True
            
        # Original synchronous loading logic for non-Pyodide environments
        # [Keep all the original logic here...]
        # Check and Create Algorithms Directory
        if not os.path.exists(self.algorithms_directory):
            os.makedirs(self.algorithms_directory)
            print(f"Created algorithms directory: {self.algorithms_directory}")

        extensions = self.get_platform_extensions()
        print(f"Platform detected: {'Pyodide' if IS_PYODIDE else platform.system()}")
        print(f"Trying extensions: {extensions}")
        print(f"Algorithms directory: {self.algorithms_directory}")
        print(f"Model name base: {self.modelNameBase}")
        print(f"Looking for model: {model}")
        
        model_found = False
        
        for extension in extensions:
            file_path = os.path.join(self.algorithms_directory, self.modelNameBase + model + extension)
            print(f"Checking for file: {file_path}")
            
            if os.path.exists(file_path):
                print(f"Found existing model file: {file_path}")
                file_size = os.path.getsize(file_path)
                print(f"File size: {file_size} bytes")
                
                print(f"Attempting to set model from existing file: {file_path}")
                success = self.set_model(model)
                print(f"set_model returned: {success}")
                if success:
                    model_found = True
                    break
                else:
                    print(f"Failed to set model from existing file: {file_path}")
            else:
                print(f"File does not exist: {file_path}")
                try:
                    url = self.modelFolderUrl + '/' + self.module + '/' + model + '/' + self.modelNameBase + model + extension
                    print(f"Attempting to download model from: {url}")
                    
                    print(f"Starting download...")
                    
                    # Check if URL is accessible first
                    try:
                        import urllib.request
                        req = urllib.request.Request(url, method='HEAD')
                        response = urllib.request.urlopen(req)
                        print(f"URL is accessible, status: {response.getcode()}")
                    except urllib.error.HTTPError as he:
                        print(f"HTTP Error {he.code}: {he.reason} for URL: {url}")
                        if he.code == 404:
                            print(f"Model file not found at: {url}")
                        continue
                    except Exception as check_e:
                        print(f"Could not check URL accessibility: {check_e}")
                        # Continue anyway, maybe the HEAD request failed but GET will work
                    
                    try:
                        urllib.request.urlretrieve(url, file_path)
                        downloaded_size = os.path.getsize(file_path)
                        print(f"Successfully downloaded model to: {file_path} (size: {downloaded_size} bytes)")
                        
                        # Verify the file was downloaded correctly
                        if downloaded_size == 0:
                            print(f"Error: Downloaded file is empty")
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            continue
                        
                        # Check if the downloaded file is actually a Python file
                        if extension == '.py':
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    first_few_lines = []
                                    for i in range(min(5, downloaded_size // 50)):  # Read first few lines
                                        line = f.readline().strip()
                                        if line:
                                            first_few_lines.append(line)
                                    print(f"First few lines of downloaded file: {first_few_lines}")
                                    
                                    # Check if it looks like a Python file
                                    content_check = any(line.startswith(('import ', 'from ', 'class ', 'def ', '#')) for line in first_few_lines)
                                    if not content_check and first_few_lines:
                                        print(f"Warning: Downloaded file doesn't look like Python code")
                                        print(f"Content preview: {first_few_lines[0][:100] if first_few_lines else 'Empty'}")
                            except Exception as read_e:
                                print(f"Error reading downloaded file: {read_e}")
                        
                        # Try to set the model
                        print(f"Attempting to set model: {model}")
                        success = self.set_model(model)
                        print(f"set_model after download returned: {success}")
                        
                        if success:
                            print(f"Model successfully set from downloaded file")
                            model_found = True
                            break
                        else:
                            print(f"Failed to set model from downloaded file: {file_path}")
                            print(f"Model object after failed set_model: {self.model}")
                            # Don't delete the file yet, maybe we can debug further
                            
                    except urllib.error.URLError as url_e:
                        print(f"URL Error during download: {url_e}")
                        continue
                    except Exception as download_e:
                        print(f"Unexpected error during download: {download_e}")
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        continue
                except Exception as e:
                    print(f"Failed to download {extension} version: {e}")
                    print(f"Exception type: {type(e)}")
                    if hasattr(e, 'code'):
                        print(f"HTTP Error Code: {e.code}")
                    if hasattr(e, 'reason'):
                        print(f"HTTP Error Reason: {e.reason}")
                    if os.path.exists(file_path):
                        print(f"Cleaning up partial download: {file_path}")
                        os.remove(file_path)  # Clean up partial download
                    continue
        
        print(f"Final result: model_found = {model_found}")
        
        if not model_found:
            available_extensions = extensions
            # Provide more detailed error information
            attempted_urls = []
            for ext in extensions:
                url = self.modelFolderUrl + '/' + self.module + '/' + model + '/' + self.modelNameBase + model + ext
                attempted_urls.append(url)
            
            error_msg = f"Could not load model '{model}' with any supported extension: {available_extensions}\n"
            error_msg += f"Attempted URLs:\n"
            for url in attempted_urls:
                error_msg += f"  - {url}\n"
            error_msg += f"Expected file pattern: {self.modelNameBase}{model}{extensions[0]}\n"
            error_msg += f"Please check if the model exists at the expected location."
            
            raise Exception(error_msg)
        
        return model_found

    async def ensure_loaded(self):
        """Ensure the model is loaded, using async loading if needed"""
        if IS_PYODIDE:
            # In Pyodide, we always use API calls, so consider it "loaded"
            self.model_loaded = True
            return True
            
        if not self.model_loaded:
            success = await self.load_model_file(self.algorithm)
            if success and self.model is not None:
                self.model_loaded = True
                return True
            else:
                raise Exception(f"Failed to load model '{self.algorithm}' asynchronously")
        return True

    def load(self, algorithm):
        """Load model synchronously"""
        if IS_PYODIDE:
            print("Pyodide environment: Using API calls, no local model loading needed")
            self.model_loaded = True
            return "API_MODE"
            
        try:
            self.load_model_file_sync(algorithm)
        except Exception as e:
           return f'The model could not be loaded correctly. Error: {str(e)}'
        
        return self.model
    
    async def load_async(self, algorithm):
        """Async version of load method"""
        if IS_PYODIDE:
            print("Pyodide environment: Using API calls, no local model loading needed")
            self.model_loaded = True
            return "API_MODE"
            
        try:
            success = await self.load_model_file(algorithm)
            if success and self.model is not None:
                self.model_loaded = True
                return self.model
            else:
                return 'The model could not be loaded correctly. Please ensure it is named properly and check that it exists.'
        except Exception as e:
           return f'The model could not be loaded correctly. Error: {str(e)}'

    def load_sync(self, algorithm):
        """Synchronous wrapper for load method"""
        if IS_PYODIDE:
            print("Pyodide environment: Using API calls, no local model loading needed")
            self.model_loaded = True
            return "API_MODE"
            
        try:
            success = self.load_model_file_sync(algorithm)
            if success and self.model is not None:
                self.model_loaded = True
                return self.model
            else:
                return f'The model could not be loaded correctly. Please ensure it is named properly and check that it exists.'
        except Exception as e:
            return f'The model could not be loaded correctly. Error: {str(e)}'