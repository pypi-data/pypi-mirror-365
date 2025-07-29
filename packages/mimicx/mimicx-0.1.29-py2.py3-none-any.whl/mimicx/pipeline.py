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

class Pipeline:

    def __init__(self, domainAlgorithm):
        self.modelFolderUrl = 'https://speedpresta.s3.us-east-1.amazonaws.com/mimicx'
        self.modelNameBase = 'mimicx_'
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

    def load_model_file(self, model):
        
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
            else:
                try:
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
