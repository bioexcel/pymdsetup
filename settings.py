"""Reader class for the config.yaml configuration file of the pymdsetup package
"""

import yaml
import os

class ConfigReader(object):
    def __init__(self, yaml_path="./conf.yaml"):
        self.yaml_path= os.path.abspath(yaml_path)
        self.properties= self.__read_yaml()

    def __read_yaml(self):
        with open(self.yaml_path, 'r') as stream:
            return yaml.load(stream)
