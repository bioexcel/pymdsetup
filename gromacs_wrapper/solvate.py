# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS solvate module

@author: pau
"""
import shutil
import os

try:
    from command_wrapper import cmd_wrapper
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.pycompss_dummies.task import task
    from pymdsetup.pycompss_dummies.constraint import constraint
    from pymdsetup.pycompss_dummies.parameter import *


class Solvate512(object):
    """Wrapper for the 5.1.2 version of the solvate module
    """

    def __init__(self, solute_structure_gro_path, output_gro_path,
                 input_top_path, output_top_path,
                 solvent_structure_gro_path="spc216.gro",
                 log_path='None', error_path='None', gmx_path='None'):
        self.solute_structure_gro_path = solute_structure_gro_path
        self.output_gro_path = output_gro_path
        self.solvent_structure_gro_path = solvent_structure_gro_path
        self.toplogy_in = input_top_path
        self.topology_out = output_top_path
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self, topin, topout):
        shutil.copy(topin, topout)
        shutil.copy(topout, "/tmp/sol.top")
        shutil.copy(self.toplogy_in, self.topology_out)
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "solvate", "-cp", self.solute_structure_gro_path,
               "-cs", self.solvent_structure_gro_path, "-o",
               self.output_gro_path, "-p", "/tmp/sol.top"]

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        shutil.copy("/tmp/sol.top", topout)

    @task(returns=dict, topin=FILE_IN, topout=FILE_OUT)
    def launchPyCOMPSs(self, top, gro, topin, topout):
        self.launch(topin, topout)
        return {'sol_gro': self.output_gro_path, 'sol_top': self.topology_out}
