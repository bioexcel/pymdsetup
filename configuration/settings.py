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

    The path for the configuration file path should be provided by an argument
    in the constructor or the 'PYMDS_CONF' environment variable.
    If none of the two is provided the default path will be './conf.yaml'
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
        if 'paths' in dp:
            if mut is None:
                dp['path'] = opj(self.properties['workflow_path'], dp['paths']['path'])
            else:
                dp['path'] = opj(self.properties['workflow_path'], mut, dp['paths']['path'])
            for key in dp['paths']:
                if key != 'path':
                    dp[key] = opj(dp['path'], dp['paths'][key])

        if 'properties' in dp:
            for key in dp['properties']:
                dp[key] = dp['properties'][key]

        dp.pop('paths', None)
        dp.pop('properties', None)

        return Dict2Obj(dp)


def str2bool(v):
    if isinstance(v, bool):
            return v
    return v.lower() in ("yes", "true", "t", "1")
