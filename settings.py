"""Settings loader module.

This module contains the classes to read the different formats of the 
configuration files.

The configuration file path should be specified in the PYMDS_CONF environment
variable.

"""

import yaml
import os


class YamlReader(object):
    """Configuration file loader for yaml format files.
    
    The path for the configuration file path should be provided via the
    'PYMDS_CONF' environment variable. Default path will be './conf.yaml'
    """
    
    def __init__(self):
        self.yaml_path = os.path.abspath('./conf.yaml')
        if os.environ.get('PYMDS_CONF') is not None:
            self.yaml_path = os.path.abspath(os.environ.get('PYMDS_CONF'))
        self.properties = self.__read_yaml()

    def __read_yaml(self):
        with open(self.yaml_path, 'r') as stream:
            return yaml.load(stream)
