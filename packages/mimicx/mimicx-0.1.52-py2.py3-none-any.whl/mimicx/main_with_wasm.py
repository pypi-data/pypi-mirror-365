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
        self.wasm_module = None
        
        # Try to load the model during initialization
        # In Pyodide, prefer async loading for WASM files
        if IS_PYODIDE:
            # Schedule async loading but don't block initialization
            print("Pyodide detected - WASM loading will be handled asynchronously")
        else:
            try:
                self.load_model_file_sync(self.algorithm)
                if self.model is not None:
                    self.model_loaded = True
            except Exception as e:
                print(f"Warning: Could not load model during initialization: {e}")

    def get_model(self):
        return self.model

    def set_model(self, algorithm):
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
                        if IS_PYODIDE:
                            raise AttributeError(f"Model '{self.algorithm}' files were found/downloaded but could not be imported. "
                                               f"This might be a WASM-only model. Try: 'await model.load_async(\"{self.algorithm}\")' "
                                               f"for WASM support, or check if a Python version exists.")
                        else:
                            raise AttributeError(f"Model '{self.algorithm}' files were found/downloaded but could not be imported. "
                                               f"Check the module structure and naming.")
                else:
                    # Loading failed completely
                    print(f"Loading failed completely. Success: {success}, Model: {self.model}")
                    if IS_PYODIDE:
                        raise AttributeError(f"Model '{self.algorithm}' could not be loaded. "
                                           f"Try: 'await model.load_async(\"{self.algorithm}\")' for WASM support, "
                                           f"or check that the model exists at the expected URL.")
                    else:
                        raise AttributeError(f"Model '{self.algorithm}' could not be loaded. "
                                           f"Check that the model exists and is accessible.")
                        
            except Exception as e:
                print(f"Exception during model loading: {str(e)}")
                if IS_PYODIDE:
                    raise AttributeError(f"Model '{self.algorithm}' could not be loaded. "
                                       f"In Pyodide environment, try: 'await model.load_async(\"{self.algorithm}\")'. "
                                       f"Error: {str(e)}")
                else:
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
    
    async def load_wasm_module(self, wasm_url, file_path):
        """Load WASM module in Pyodide environment"""
        if not IS_PYODIDE:
            print("WASM loading only supported in Pyodide environment")
            return None
            
        try:
            print(f"Fetching WASM module from: {wasm_url}")
            # Fetch the WASM file
            response = await pyfetch(wasm_url)
            if response.status == 200:
                # Get the WASM bytes
                wasm_bytes = await response.bytes()
                
                # Write to file system for caching
                with open(file_path, 'wb') as f:
                    f.write(wasm_bytes.to_py())
                print(f"WASM file cached to: {file_path}")
                
                # Load the WASM module using Pyodide's WebAssembly support
                wasm_module = await js.WebAssembly.instantiate(wasm_bytes)
                print("WASM module instantiated successfully")
                return wasm_module
                
            else:
                print(f"Failed to fetch WASM file: {response.status}")
                return None
                
        except Exception as e:
            print(f"Error loading WASM module: {e}")
            return None

    async def load_existing_wasm(self, file_path):
        """Load existing WASM file in Pyodide environment"""
        if not IS_PYODIDE:
            return None
            
        try:
            with open(file_path, 'rb') as f:
                wasm_bytes = f.read()
            
            # Convert to JavaScript ArrayBuffer for WebAssembly
            js_array_buffer = js.ArrayBuffer.new(len(wasm_bytes))
            js_uint8_array = js.Uint8Array.new(js_array_buffer)
            
            # Copy bytes to JavaScript array
            for i, byte in enumerate(wasm_bytes):
                js_uint8_array[i] = byte
            
            wasm_module = await js.WebAssembly.instantiate(js_array_buffer)
            print("Existing WASM module instantiated successfully")
            return wasm_module
            
        except Exception as e:
            print(f"Error loading existing WASM: {e}")
            return None

    def get_platform_extensions(self):
        """Get appropriate file extensions based on the current platform"""
        if IS_PYODIDE:
            # In Pyodide, prioritize WASM but keep Python as fallback
            return ['.wasm', '.py']
        elif platform.system() == "Windows":
            return ['windows.pyd', '.py']
        elif platform.system() == "Darwin":
            return ['.cpython-39-darwin.so', '.py']
        else:
            return ['.cpython-311-x86_64-linux-gnu.so', '.py']

    async def load_model_file(self, model):
        """Async version that properly handles WASM in Pyodide"""
        
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

                if extension == '.wasm' and IS_PYODIDE:
                    # Load existing WASM file asynchronously
                    wasm_module = await self.load_existing_wasm(file_path)
                    if wasm_module:
                        self.wasm_module = wasm_module
                        # After loading WASM, try to set up the Python interface
                        success = self.set_model(model)
                        if success:
                            return True
                    else:
                        # If WASM loading failed, continue to try other extensions
                        continue
                else:
                    success = self.set_model(model)
                    if success:
                        return True
            else:
                try:
                    url = self.modelFolderUrl + '/' + self.module + '/' + model + '/' + self.modelNameBase + model + extension
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
        """Synchronous version - limited WASM support in Pyodide"""
        
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
                
                # For WASM files in Pyodide, we can't handle them synchronously
                # but we should inform the user instead of silently skipping
                if extension == '.wasm' and IS_PYODIDE:
                    print("WASM file found but requires async loading in Pyodide. Use load_async() or ensure_loaded().")
                    print("Continuing with Python fallback...")
                    continue
                
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
                    
                    # Skip WASM download in sync mode for Pyodide, but inform user
                    if extension == '.wasm' and IS_PYODIDE:
                        print("WASM download requires async loading in Pyodide. Use load_async() for WASM support.")
                        print("Trying next extension...")
                        continue
                    
                    print(f"Starting download...")
                    urllib.request.urlretrieve(url, file_path)
                    downloaded_size = os.path.getsize(file_path)
                    print(f"Successfully downloaded model to: {file_path} (size: {downloaded_size} bytes)")
                    
                    success = self.set_model(model)
                    print(f"set_model after download returned: {success}")
                    if success:
                        model_found = True
                        break
                    else:
                        print(f"Failed to set model from downloaded file: {file_path}")
                except Exception as e:
                    print(f"Failed to download {extension} version: {e}")
                    print(f"Exception type: {type(e)}")
                    if os.path.exists(file_path):
                        print(f"Cleaning up partial download: {file_path}")
                        os.remove(file_path)  # Clean up partial download
                    continue
        
        print(f"Final result: model_found = {model_found}")
        
        if not model_found:
            if IS_PYODIDE:
                raise Exception(f"Could not load model '{model}' synchronously. "
                              f"For WASM support in Pyodide, use 'await model.load_async(\"{model}\")' instead.")
            else:
                available_extensions = [ext for ext in extensions if not (ext == '.wasm' and IS_PYODIDE)]
                raise Exception(f"Could not load model '{model}' with any supported extension: {available_extensions}")
        
        return model_found

    async def ensure_loaded(self):
        """Ensure the model is loaded, using async loading if needed"""
        if not self.model_loaded:
            if IS_PYODIDE:
                success = await self.load_model_file(self.algorithm)
                if success and self.model is not None:
                    self.model_loaded = True
                    return True
                else:
                    raise Exception(f"Failed to load model '{self.algorithm}' asynchronously")
            else:
                success = self.load_model_file_sync(self.algorithm)
                if success and self.model is not None:
                    self.model_loaded = True
                    return True
                else:
                    raise Exception(f"Failed to load model '{self.algorithm}' synchronously")
        return True

    def load(self, algorithm):
        """Load model - warns about WASM limitations in Pyodide"""
        try:
            if IS_PYODIDE:
                print("Warning: Synchronous loading in Pyodide has limited WASM support.")
                print("For full WASM support, use 'await model.load_async(algorithm)' instead.")
            
            self.load_model_file_sync(algorithm)
        except Exception as e:
           return f'The model could not be loaded correctly. Error: {str(e)}'
        
        return self.model
    
    async def load_async(self, algorithm):
        """Async version of load method with full WASM support"""
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
            raise RuntimeError("No WASM module loaded. Use 'await model.load_async()' first.")