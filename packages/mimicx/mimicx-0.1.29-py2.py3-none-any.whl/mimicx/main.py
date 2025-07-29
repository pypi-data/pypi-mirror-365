import js
import pyodide
from pyodide.http import pyfetch
import asyncio
import urllib.request
import os
import platform
import re
import base64
from pathlib import Path
from typing import Union, Any
import numpy as np
import importlib
from pathlib import Path

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
    
    async def load_wasm_module(self, wasm_url, file_path):
        """Load WASM module in Pyodide environment"""
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
                # Method 1: Direct instantiation
                wasm_module = await js.WebAssembly.instantiate(wasm_bytes)
                return wasm_module
                
            else:
                print(f"Failed to fetch WASM file: {response.status}")
                return None
                
        except Exception as e:
            print(f"Error loading WASM module: {e}")
            return None

    async def load_model_file(self, model):
        
        # Check and Create Algorithms Directory
        if not os.path.exists(self.algorithms_directory):
            os.makedirs(self.algorithms_directory)

        # Determine file extension based on platform
        if platform.system() == "Windows":
            extensions = ['windows.pyd','.py']
        elif platform.system() == "Darwin":
            extensions = ['.cpython-39-darwin.so','.py']
        elif platform.system() == "Emscripten":
            extensions = ['.wasm', '.py']
        else:
            extensions = ['.cpython-311-x86_64-linux-gnu.so','.py']
        
        for extension in extensions:
            
            file_path = os.path.join(self.algorithms_directory, self.modelNameBase +  model + extension)
            
            if os.path.exists(file_path):

                if extension == '.wasm':
                    # Load existing WASM file
                    with open(file_path, 'rb') as f:
                        wasm_bytes = f.read()
                    try:
                        wasm_module = await js.WebAssembly.instantiate(wasm_bytes)
                        # Store WASM module for later use
                        self.wasm_module = wasm_module
                    except Exception as e:
                        print(f"Error instantiating existing WASM: {e}")
                        continue

                self.set_model(model)

            else:
                try:

                    if extension == '.wasm':
                        wasm_module = await self.load_wasm_module(url, file_path)
                        if wasm_module:
                            self.wasm_module = wasm_module
                            self.set_model(model)
                            return
                    else:
                        url = self.modelFolderUrl + '/' + self.module + '/'  + model + '/' + self.modelNameBase + model + extension
                        urllib.request.urlretrieve(url, file_path)
                        self.set_model(model)
                except:
                    pass

    def load(self, algorithm):
        try:
            self.load_model_file(algorithm)
        except:
           return 'The model could not be loaded correctly. Please ensure it is named properly and check that it exists.'
        
        return self.model
    

    def load_sync(self, algorithm):
        """Synchronous wrapper for load method"""
        try:
            # Create event loop if it doesn't exist
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async load method
            if loop.is_running():
                # If loop is already running, create a task
                task = asyncio.create_task(self.load(algorithm))
                return task
            else:
                # Run the coroutine
                return loop.run_until_complete(self.load(algorithm))
                
        except Exception as e:
            return f'The model could not be loaded correctly. Error: {str(e)}'

    def call_wasm_function(self, function_name, *args):
        """Call a function from the loaded WASM module"""
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
