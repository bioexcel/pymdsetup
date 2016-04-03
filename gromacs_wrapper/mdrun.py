# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS mdrun module

@author: pau
"""
from pymdsetup.command_wrapper import cmd_wrapper
import os.path as op


class Mdrun512(object):
    """Wrapper for the 5.1.2 version of the mdrun module
    """

    def __init__(self, tpr_path, output_trr_path, gro_path, output_edr_path,
                 output_xtc_path=None, output_cpt_path=None, log_path=None,
                 error_path=None, gmx_path=None):
        self.tpr_path = tpr_path
        self.gro_path = gro_path
        self.output_trr_path = output_trr_path
        self.output_edr_path = output_edr_path
        self.output_xtc_path = output_xtc_path
        self.output_cpt_path = output_cpt_path
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = [gmx, "mdrun", "-s", self.tpr_path, "-o", self.output_trr_path,
               "-c", self.gro_path, "-e", self.output_edr_path]
        if self.output_xtc_path is not None:
            cmd.append("-x")
            cmd.append(self.output_xtc_path)
        if self.output_cpt_path is not None:
            cmd.append("-cpo")
            cmd.append(self.output_cpt_path)

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        command.move_file_output("md.log", op.dirname(self.output_trr_path))
