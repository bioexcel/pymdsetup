# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS pdb2gmx module

@author: pau
"""

class pdb2gmx512(object):
    """Wrapper for the 5.1.2 version of the pdb2gmx module
    """
    
    def __init__(self, structure_file_path, output_file_path, 
                 log_file_path=None, water_type='spce', force_field='oplsaa', 
                 gmx_path=""):
        self.structure_file_path =  structure_file_path
        self.output_file_path = output_file_path
        self.water_type = water_type
        self.force_field = force_field
        self.gmx_path = gmx_path
        self.log_file_path = log_file_path

    def launch(self):
        pass