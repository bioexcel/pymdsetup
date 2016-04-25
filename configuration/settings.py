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
from os.path import join as opj


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

    def step_prop(self, step, mut=None):

        class Dict2Obj(object):
            def __init__(self, dictionary):
                for key in dictionary:
                    setattr(self, key, dictionary[key])

        self.properties = self._read_yaml()
        dp = self.properties[step]
        if mut is None:
            dp['path'] = opj(self.properties['workflow_path'], dp['path'])
        else:
            dp['path'] = opj(self.properties['workflow_path'], mut, dp['path'])
        for key in dp:
            if key != 'path':
                dp[key] = opj(dp['path'], dp[key])

        return Dict2Obj(dp)
