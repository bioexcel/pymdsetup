# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS genion module

@author: pau
"""
from pymdsetup.command_wrapper import cmd_wrapper


class Genion512(object):
    """Wrapper for the 5.1.2 version of the genion module
    """

    def __init__(self, tpr_path, output_gro_path, top_path,
                 replaced_group="SOL", log_path=None, error_path=None,
                 gmx_path=None):
        self.tpr_path = tpr_path
        self.output_gro_path = output_gro_path
        self.top_path = top_path
        self.replaced_group = replaced_group
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = ["echo", self.replaced_group, "|", gmx, "genion", "-s",
               self.tpr_path, "-o", self.output_gro_path, "-p", self.top_path,
               "-neutral"]

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
