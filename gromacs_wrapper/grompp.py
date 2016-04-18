# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS grompp module

@author: pau
"""
from command_wrapper import cmd_wrapper
import os.path as op

try:
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.task import task
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.pycompss_dummies.task import task
    from pymdsetup.pycompss_dummies.constraint import constraint
    from pymdsetup.pycompss_dummies.parameter import *


class Grompp512(object):
    """Wrapper for the 5.1.2 version of the pdb2gmx module
    """

    def __init__(self, mdp_path, gro_path, top_path, output_tpr_path,
                 cpt_path='None', log_path='None', error_path='None',
                 gmx_path='None'):
        self.mdp_path = mdp_path
        self.gro_path = gro_path
        self.top_path = top_path
        self.output_tpr_path = output_tpr_path
        self.cpt_path = cpt_path
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "grompp", "-f", self.mdp_path, "-c", self.gro_path, "-p",
               self.top_path, "-o", self.output_tpr_path]
        if self.cpt_path != 'None':
            cmd.append("-t")
            cmd.append(self.cpt_path)

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        command.move_file_output("mdout.mdp", op.dirname(self.output_tpr_path))

    @task(returns=dict)
    def launchPyCOMPSs(self, sol, gro = 'None'):
        #self.launch()
        return {'gpp_tpr': self.output_tpr_path}
