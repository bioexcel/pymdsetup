# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS pdb2gmx module

@author: pau
"""


import os.path as osp
import re
import cmd_wrapper


class Pdb2gmx512(object):
    """Wrapper for the 5.1.2 version of the pdb2gmx module
    """

    def __init__(self, structure_path, output_path, 
                 water_type='spce', force_field='oplsaa', 
                 log_path=None, error_path=None, gmx_path=None):
        self.structure_path = osp.abspath(structure_path)
        self.output_path = osp.abspath(output_path)
        self.water_type = water_type
        self.force_field = force_field
        self.gmx_path = None if gmx_path is None else osp.abspath(gmx_path)
        self.log_path = None if log_path is None else osp.abspath(log_path)
        self.error_path = None if log_path is None else osp.abspath(error_path)

    def launch(self):
        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = [gmx,"pdb2gmx", "-f", self.structure_file_path,
               "-o",self.output_file_path, "-water ",self.water_type,
               "-ff", self.force_field]

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
