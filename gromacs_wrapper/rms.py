# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS rms module

@author: pau
"""
from pymdsetup.command_wrapper import cmd_wrapper
import shutil

try:
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.task import task
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.pycompss_dummies.task import task
    from pymdsetup.pycompss_dummies.constraint import constraint
    from pymdsetup.pycompss_dummies.parameter import *


class Rms512(object):
    """Wrapper for the 5.1.2 version of the rms module
    """

    def __init__(self, input_ref_struct, input_traj, output_xvg,
                 log_path='None', error_path='None', gmx_path='None'):
        self.input_ref_struct = input_ref_struct
        self.input_traj = input_traj
        self.output_xvg = output_xvg
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path
        self.rmsd = 'None'

    def launch(self):
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = ["echo", "0 0", "|",
               gmx, "rms", "-s", self.input_ref_struct, "-f", self.input_traj,
               "-o", self.output_xvg]
        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        with open(self.output_xvg) as xvg:
            for line in xvg:
                pass
            self.rmsd = float(line.split()[-1])
        return float(self.rmsd)

    @task(returns=float)
    def launchPyCOMPSs(self):
        return self.launch()
