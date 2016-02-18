"""Settings loader module.

This module contains the different classes to read the configuration files.
The configuration file path should be specified in the PYMDSETUP

"""

import yaml
import os


class YamlReader(object):
    def __init__(self, yaml_path="./conf.yaml"):
        self.yaml_path = os.path.abspath(yaml_path)
        self.properties = self.__read_yaml()

    def __read_yaml(self):
        with open(self.yaml_path, 'r') as stream:
            return yaml.load(stream)
