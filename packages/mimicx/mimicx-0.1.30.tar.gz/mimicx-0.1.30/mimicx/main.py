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
        self.load_model_file(self.algorithm)

    def get_model(self):
        return self.model

    def set_model(self, algorithm):
        if algorithm:
            module_name = f"mimicx_{algorithm}"
            class_name = f"Mimicx{algorithm.replace('_', ' ').title().replace(' ', '')}"

            try:
                module = importlib.import_module(f".{module_name}", package=__package__)
            except ImportError:
                module = importlib.import_module(module_name)

            self.model = getattr(module, class_name)()

    def __getattr__(self, attr):
        return getattr(self.model, attr)
    
    async def load_wasm_module_http(self, wasm_url, file_path):
        """Load WASM module using standard HTTP libraries (non-pyodide)"""
        try:
            # Use urllib for HTTP requests instead of pyfetch
            urllib.request.urlretrieve(wasm_url, file_path)
            
            # Read the WASM file
            with open(file_path, 'rb') as f:
                wasm_bytes = f.read()
            
            print(f"WASM file downloaded and saved to {file_path}")
            # Note: Without pyodide's js.WebAssembly, we can't instantiate WASM modules
            # This would need to be handled by the calling environment
            return wasm_bytes
                
        except Exception as e:
            print(f"Error loading WASM module: {e}")
            return None

    def load_wasm_module_sync(self, wasm_url, file_path):
        """Synchronous version of WASM module loading"""
        try:
            urllib.request.urlretrieve(wasm_url, file_path)
            
            with open(file_path, 'rb') as f:
                wasm_bytes = f.read()
            
            print(f"WASM file downloaded and saved to {file_path}")
            return wasm_bytes
                
        except Exception as e:
            print(f"Error loading WASM module: {e}")
            return None

    async def load_model_file(self, model):
        
        # Check and Create Algorithms Directory
        if not os.path.exists(self.algorithms_directory):
            os.makedirs(self.algorithms_directory)

        # Determine file extension based on platform
        # Remove Emscripten check since we're removing pyodide dependency
        if platform.system() == "Windows":
            extensions = ['windows.pyd','.py']
        elif platform.system() == "Darwin":
            extensions = ['.cpython-39-darwin.so','.py']
        else:
            extensions = ['.cpython-311-x86_64-linux-gnu.so','.py']
        
        for extension in extensions:
            
            file_path = os.path.join(self.algorithms_directory, self.modelNameBase +  model + extension)
            
            if os.path.exists(file_path):
                self.set_model(model)
                return

            else:
                try:
                    url = self.modelFolderUrl + '/' + self.module + '/'  + model + '/' + self.modelNameBase + model + extension
                    urllib.request.urlretrieve(url, file_path)
                    self.set_model(model)
                    return
                except:
                    pass

    def load_model_file_sync(self, model):
        """Synchronous version of load_model_file"""
        
        # Check and Create Algorithms Directory
        if not os.path.exists(self.algorithms_directory):
            os.makedirs(self.algorithms_directory)

        # Determine file extension based on platform
        if platform.system() == "Windows":
            extensions = ['windows.pyd','.py']
        elif platform.system() == "Darwin":
            extensions = ['.cpython-39-darwin.so','.py']
        else:
            extensions = ['.cpython-311-x86_64-linux-gnu.so','.py']
        
        for extension in extensions:
            
            file_path = os.path.join(self.algorithms_directory, self.modelNameBase +  model + extension)
            
            if os.path.exists(file_path):
                self.set_model(model)
                return

            else:
                try:
                    url = self.modelFolderUrl + '/' + self.module + '/'  + model + '/' + self.modelNameBase + model + extension
                    urllib.request.urlretrieve(url, file_path)
                    self.set_model(model)
                    return
                except:
                    pass

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
            self.load_model_file_sync(algorithm)
            return self.model
        except Exception as e:
            return f'The model could not be loaded correctly. Error: {str(e)}'
    
    def load_wasm_file(self, wasm_url, file_path):
        """Download WASM file (without instantiation)"""
        try:
            return self.load_wasm_module_sync(wasm_url, file_path)
        except Exception as e:
            print(f"Error downloading WASM file: {e}")
            return None