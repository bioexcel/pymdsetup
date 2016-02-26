# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS pdb2gmx module

@author: pau
"""

import subprocess
import os.path as osp
import re
 

class pdb2gmx512(object):
    """Wrapper for the 5.1.2 version of the pdb2gmx module
    """
    
    def __init__(self, structure_path, output_path, 
                 water_type='spce', force_field='oplsaa', 
                 log_path=None, gmx_path=None):
        self.structure_path = osp.abspath(structure_path)
        self.output_path = osp.abspath(output_path)
        self.water_type = water_type
        self.force_field = force_field
        self.gmx_path = None if gmx_path is None else osp.abspath(gmx_path)
        self.log_path = None if log_path is None else osp.abspath(log_path)

    def launch(self):
        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = [gmx,"pdb2gmx", "-f", self.structure_file_path,
        "-o",self.output_file_path, "-water ",self.water_type,
        "-ff", self.force_field]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, 
                                   universal_newlines=True)
        out, err = process.communicate()
        
        #Write output to log_file
        if self.log_path is not None:
            with open(self.log_path, 'w') as log_file:
                log_file.writte(out)
                
        #Return the total charge of the molecule
        return float(
           re.search(r'Total charge ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)',
                     out, re.MULTILINE))
                  
        