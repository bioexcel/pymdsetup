# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS grommpp module

@author: pau
"""
import cmd_wrapper


class Grommpp512(object):
    """Wrapper for the 5.1.2 version of the pdb2gmx module
    """

    def __init__(self, mdp_path, gro_path, top_path, output_tpr_path,
                 cpt_path=None, log_path=None, error_path=None, gmx_path=None):
        self.mdp_path = mdp_path
        self.gro_path = gro_path
        self.top_path = top_path
        self.output_tpr_path = output_tpr_path
        self.cpt_path = cpt_path
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = [gmx, "grommpp", "-f", self.mdp_path, "-c", self.gro_path, "-p",
               self.top_path, "-o", self.output_tpr_path]
        if self.cpt_path is not None:
            cmd.append("-t")
            cmd.append(self.cpt_path)

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
