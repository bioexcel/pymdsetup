# -*- coding: utf-8 -*-
"""Settings loader module.

This module contains the classes to read the different formats of the 
configuration files.

The configuration file path should be specified in the PYMDS_CONF environment
variable.

@author: pau
"""

import yaml
import os


class YamlReader(object):
    """Configuration file loader for yaml format files.
    
    The path for the configuration file path should be provided via the
    'PYMDS_CONF' environment variable. Default path will be './conf.yaml'
    """
    
    def __init__(self, yaml_path=None):
        if yaml_path is not None:
            self.yaml_path = yaml_path
        elif os.environ.get('PYMDS_CONF') is not None:
            self.yaml_path = os.environ.get('PYMDS_CONF')
        else:
            self.yaml_path = 'conf.yaml'
            
        self.properties = self._read_yaml()

    def _read_yaml(self):
        with open(self.yaml_path, 'r') as stream:
            return yaml.load(stream)
