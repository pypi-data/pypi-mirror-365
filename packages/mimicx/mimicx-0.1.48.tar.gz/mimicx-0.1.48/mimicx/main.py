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
        print("Running in Pyodide environment - Python support enabled")
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
        
        # Try to load the model during initialization
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

    def get_platform_extensions(self):
        """Get appropriate file extensions based on the current platform"""
        if IS_PYODIDE:
            # In Pyodide, only use Python files
            return ['.py']
        elif platform.system() == "Windows":
            return ['windows.pyd', '.py']
        elif platform.system() == "Darwin":
            return ['.cpython-39-darwin.so', '.py']
        else:
            return ['.cpython-311-x86_64-linux-gnu.so', '.py']

    async def load_model_file(self, model):
        """Async version for downloading files"""
        
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

                    if IS_PYODIDE:
                        # Use pyfetch for async download in Pyodide
                        response = await pyfetch(url)
                        if response.status == 200:
                            content = await response.text()
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"Successfully downloaded model to: {file_path}")
                        else:
                            print(f"Failed to download: HTTP {response.status}")
                            continue
                    else:
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
        """Synchronous version"""
        
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
            available_extensions = extensions
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
        """Load model synchronously"""
        try:
            self.load_model_file_sync(algorithm)
        except Exception as e:
           return f'The model could not be loaded correctly. Error: {str(e)}'
        
        return self.model
    
    async def load_async(self, algorithm):
        """Async version of load method"""
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