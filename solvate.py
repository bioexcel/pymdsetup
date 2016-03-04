# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS solvate module

@author: pau
"""
import cmd_wrapper

class Solvate512(object):
    """Wrapper for the 5.1.2 version of the solvate module
    """

    def __init__(self, solute_structure_gro_path, output_gro_path,
                 solvent_structure_gro_path, log_path=None, error_path=None,
                 gmx_path=None):
        self.solute_structure_gro_path = solute_structure_gro_path
        self.output_path = output_gro_path
        self.distance_to_molecule = distance_to_molecule 
        self.box_type = box_type
        self.center_molecule = center_molecule
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = [gmx,"pdb2gmx", "-f", self.structure_gro_path,
               "-o",self.output_gro_path, "-d ",self.distance_to_molecule,
               "-bt", self.box_type]
        if self.center_molecule: cmd.append("-c")

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
