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

# Detect if running in Pyodide environment
IS_PYODIDE = "pyodide" in sys.modules or hasattr(sys, "_getframe") and "pyodide" in str(sys._getframe())

# Import pyodide-specific modules only if in Pyodide environment
if IS_PYODIDE:
    try:
        import js
        import pyodide
        from pyodide.http import pyfetch
        print("Running in Pyodide environment - WASM support enabled")
    except ImportError:
        print("Pyodide detected but imports failed")
        IS_PYODIDE = False

class Model:

    def __init__(self, domainAlgorithm):
        self.modelFolderUrl = 'https://speedpresta.s3.us-east-1.amazonaws.com/mimicx'
        self.modelNameBase = 'mimicx_'
        
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
        
        # Try to load the model synchronously during initialization
        try:
            self.load_model_file_sync(self.algorithm)
            if self.model is not None:
                self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load model during initialization: {e}")
            # Don't raise exception here, allow lazy loading

    def get_model(self):
        return self.model

    def set_model(self, algorithm):
        if algorithm:
            module_name = f"mimicx_{algorithm}"
            class_name = f"Mimicx{algorithm.replace('_', ' ').title().replace(' ', '')}"

            try:
                # Try relative import first
                module = importlib.import_module(f".{module_name}", package=__package__)
            except ImportError:
                try:
                    # Try absolute import
                    module = importlib.import_module(module_name)
                except ImportError as e:
                    print(f"Failed to import module '{module_name}': {e}")
                    return False

            try:
                self.model = getattr(module, class_name)()
                print(f"Successfully loaded model: {class_name}")
                return True
            except AttributeError as e:
                print(f"Class '{class_name}' not found in module '{module_name}': {e}")
                return False
            except Exception as e:
                print(f"Error instantiating class '{class_name}': {e}")
                return False
        return False

    def __getattr__(self, attr):
        # Check if model is loaded, if not try to load it
        if self.model is None and not self.model_loaded:
            print(f"Model not loaded, attempting to load algorithm: {self.algorithm}")
            
            # Try async loading first if in Pyodide environment
            if IS_PYODIDE:
                try:
                    # Create a coroutine for async loading
                    import asyncio
                    
                    async def async_load():
                        success = await self.load_model_file(self.algorithm)
                        if success and self.model is not None:
                            self.model_loaded = True
                        return success
                    
                    # Try to run the async loading
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is running, we need to handle this differently
                            # For now, fall back to sync loading
                            print("Event loop running, falling back to sync loading")
                            success = self.load_model_file_sync(self.algorithm)
                        else:
                            success = loop.run_until_complete(async_load())
                    except RuntimeError:
                        # No event loop, create one
                        success = asyncio.run(async_load())
                    
                    if success and self.model is not None:
                        self.model_loaded = True
                
                except Exception as e:
                    print(f"Async loading failed, trying sync: {e}")
                    try:
                        success = self.load_model_file_sync(self.algorithm)
                        if success and self.model is not None:
                            self.model_loaded = True
                    except Exception as sync_e:
                        raise AttributeError(f"Could not load model and attribute '{attr}' not found. Async error: {e}, Sync error: {sync_e}")
            else:
                # Non-Pyodide environment, use sync loading
                try:
                    success = self.load_model_file_sync(self.algorithm)
                    if success and self.model is not None:
                        self.model_loaded = True
                except Exception as e:
                    raise AttributeError(f"Could not load model and attribute '{attr}' not found. Error: {e}")
        
        # If model is still None after loading attempt, raise clear error
        if self.model is None:
            raise AttributeError(f"Model failed to load. Cannot access attribute '{attr}'. "
                               f"Please check that the algorithm '{self.algorithm}' exists and is properly named.")
        
        # Check if the attribute exists on the model
        if hasattr(self.model, attr):
            return getattr(self.model, attr)
        else:
            raise AttributeError(f"'{type(self.model).__name__}' object has no attribute '{attr}'")
    
    async def load_wasm_module(self, wasm_url, file_path):
        """Load WASM module in Pyodide environment"""
        if not IS_PYODIDE:
            print("WASM loading only supported in Pyodide environment")
            return None
            
        try:
            # Fetch the WASM file
            response = await pyfetch(wasm_url)
            if response.status == 200:
                # Get the WASM bytes
                wasm_bytes = await response.bytes()
                
                # Write to file system (optional, for caching)
                with open(file_path, 'wb') as f:
                    f.write(wasm_bytes.to_py())
                
                # Load the WASM module using Pyodide's WebAssembly support
                wasm_module = await js.WebAssembly.instantiate(wasm_bytes)
                return wasm_module
                
            else:
                print(f"Failed to fetch WASM file: {response.status}")
                return None
                
        except Exception as e:
            print(f"Error loading WASM module: {e}")
            return None

    def download_file_sync(self, url, file_path):
        """Synchronous file download that works in both Pyodide and regular Python"""
        try:
            if IS_PYODIDE:
                # In Pyodide, use pyodide.http.open_url for synchronous downloads
                import pyodide.http
                response = pyodide.http.open_url(url)
                
                if hasattr(response, 'read'):
                    # It's a file-like object
                    content = response.read()
                else:
                    # It's already the content
                    content = response
                
                # Write content to file
                if isinstance(content, str):
                    with open(file_path, 'w') as f:
                        f.write(content)
                else:
                    with open(file_path, 'wb') as f:
                        f.write(content)
                
                print(f"Successfully downloaded (Pyodide) to: {file_path}")
                return True
            else:
                # Regular Python environment
                urllib.request.urlretrieve(url, file_path)
                print(f"Successfully downloaded to: {file_path}")
                return True
                
        except Exception as e:
            print(f"Download failed: {e}")
            return False
        """Get appropriate file extensions based on the current platform"""
        if IS_PYODIDE:
            return ['.wasm', '.py']
        elif platform.system() == "Windows":
            return ['windows.pyd', '.py']
        elif platform.system() == "Darwin":
            return ['.cpython-39-darwin.so', '.py']
        else:
            return ['.cpython-311-x86_64-linux-gnu.so', '.py']

    async def load_model_file(self, model):
        
        # Check and Create Algorithms Directory
        if not os.path.exists(self.algorithms_directory):
            os.makedirs(self.algorithms_directory)

        extensions = self.get_platform_extensions()
        print(f"Platform detected: {'Pyodide' if IS_PYODIDE else platform.system()}")
        print(f"Trying extensions: {extensions}")
        
        for extension in extensions:
            
            file_path = os.path.join(self.algorithms_directory, self.modelNameBase +  model + extension)
            
            if os.path.exists(file_path):
                print(f"Found existing model file: {file_path}")

                if extension == '.wasm' and IS_PYODIDE:
                    # Load existing WASM file
                    with open(file_path, 'rb') as f:
                        wasm_bytes = f.read()
                    try:
                        wasm_module = await js.WebAssembly.instantiate(wasm_bytes)
                        # Store WASM module for later use
                        self.wasm_module = wasm_module
                        print("WASM module instantiated successfully")
                    except Exception as e:
                        print(f"Error instantiating existing WASM: {e}")
                        continue

                success = self.set_model(model)
                if success:
                    return True

            else:
                try:
                    url = self.modelFolderUrl + '/' + self.module + '/'  + model + '/' + self.modelNameBase + model + extension
                    print(f"Attempting to download model from: {url}")

                    if extension == '.wasm' and IS_PYODIDE:
                        wasm_module = await self.load_wasm_module(url, file_path)
                        if wasm_module:
                            self.wasm_module = wasm_module
                            success = self.set_model(model)
                            if success:
                                return True
                    else:
                        # Use urllib for non-WASM files or non-Pyodide environments
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
        """Synchronous version of load_model_file"""
        
        # Check and Create Algorithms Directory
        if not os.path.exists(self.algorithms_directory):
            os.makedirs(self.algorithms_directory)

        extensions = self.get_platform_extensions()
        print(f"Platform detected: {'Pyodide' if IS_PYODIDE else platform.system()}")
        print(f"Trying extensions: {extensions}")
        
        model_found = False
        
        for extension in extensions:
            file_path = os.path.join(self.algorithms_directory, self.modelNameBase +  model + extension)
            
            if os.path.exists(file_path):
                print(f"Found existing model file: {file_path}")
                
                # For WASM files in Pyodide, we can load them but can't instantiate synchronously
                if extension == '.wasm' and IS_PYODIDE:
                    print("WASM file found - will be available for async instantiation")
                    # Still try to set the model in case there's a Python fallback
                    success = self.set_model(model)
                    if success:
                        model_found = True
                        break
                else:
                    success = self.set_model(model)
                    if success:
                        model_found = True
                        break
            else:
                try:
                    url = self.modelFolderUrl + '/' + self.module + '/'  + model + '/' + self.modelNameBase + model + extension
                    print(f"Attempting to download model from: {url}")
                    
                    # Download the file using appropriate method
                    download_success = self.download_file_sync(url, file_path)
                    
                    if download_success:
                        if extension == '.wasm' and IS_PYODIDE:
                            print("WASM file downloaded - will be available for async instantiation")
                            # Try to set model (might have Python component)
                            success = self.set_model(model)
                            if success:
                                model_found = True
                                break
                        else:
                            success = self.set_model(model)
                            if success:
                                model_found = True
                                break
                    
                except Exception as e:
                    print(f"Failed to download {extension} version: {e}")
                    if os.path.exists(file_path):
                        os.remove(file_path)  # Clean up partial download
                    continue
        
        if not model_found:
            raise Exception(f"Could not load model '{model}' with any supported extension: {extensions}")
        
        return model_found

    def load(self, algorithm):
        try:
            # Use synchronous version by default
            self.load_model_file_sync(algorithm)
        except:
           return 'The model could not be loaded correctly. Please ensure it is named properly and check that it exists.'
        
        return self.model
    
    async def load_async(self, algorithm):
        """Async version of load method"""
        try:
            await self.load_model_file(algorithm)
        except:
           return 'The model could not be loaded correctly. Please ensure it is named properly and check that it exists.'
        
        return self.model

    def load_sync(self, algorithm):
        """Synchronous wrapper for load method"""
        try:
            success = self.load_model_file_sync(algorithm)
            if success and self.model is not None:
                self.model_loaded = True
                return self.model
            else:
                return f'The model could not be loaded correctly. Please ensure it is named properly and check that it exists.'
        except Exception as e:
            return f'The model could not be loaded correctly. Error: {str(e)}'

    def call_wasm_function(self, function_name, *args):
        """Call a function from the loaded WASM module"""
        if not IS_PYODIDE:
            raise RuntimeError("WASM functionality only available in Pyodide environment")
            
        if hasattr(self, 'wasm_module') and self.wasm_module:
            try:
                # Access the WASM instance
                instance = self.wasm_module.instance
                exports = instance.exports
                
                if hasattr(exports, function_name):
                    func = getattr(exports, function_name)
                    return func(*args)
                else:
                    raise AttributeError(f"Function '{function_name}' not found in WASM module")
            except Exception as e:
                raise RuntimeError(f"Error calling WASM function: {e}")
        else:
            raise RuntimeError("No WASM module loaded")
    
    async def load_async_with_fallback(self, algorithm=None):
        """Async loading with proper fallback handling"""
        if algorithm is None:
            algorithm = self.algorithm
            
        try:
            # Try async loading first
            success = await self.load_model_file(algorithm)
            if success and self.model is not None:
                self.model_loaded = True
                return self.model
        except Exception as e:
            print(f"Async loading failed: {e}")
        
        # Fall back to sync loading
        try:
            success = self.load_model_file_sync(algorithm)
            if success and self.model is not None:
                self.model_loaded = True
                return self.model
        except Exception as e:
            print(f"Sync loading also failed: {e}")
            
        return None