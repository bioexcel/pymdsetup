# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS pdb2gmx module

@author: pau
"""
import os
import shutil

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


class Pdb2gmx512(object):
    """Wrapper for the 5.1.2 version of the pdb2gmx module
    """

    def __init__(self, structure_pdb_path, output_path, output_top_path,
                 water_type='spce', force_field='oplsaa', ignh=False,
                 log_path='None', error_path='None', gmx_path='None'):
        self.structure_pdb_path = structure_pdb_path
        self.output_path = output_path
        self.output_top_path = output_top_path
        self.water_type = water_type
        self.force_field = force_field
        self.ignh = ignh
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "pdb2gmx", "-f", self.structure_pdb_path,
               "-o", self.output_path, "-p", self.output_top_path, "-water",
               self.water_type, "-ff", self.force_field]

        if self.ignh:
            cmd.append("-ignh")

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

        #Move posre itp files to the topology directory
        filelist = [f for f in os.listdir(".") if f.startswith("posre") and
                    f.endswith(".itp")]

        for f in filelist:
            if not os.path.exists(os.path.join(
                                  os.path.dirname(self.output_top_path), f)):
                shutil.move(f, os.path.dirname(self.output_top_path))

    @task(returns=dict)
    def launchPyCOMPSs(self, pdb_path):
        self.launch()
        return {'p2g_gro': self.output_path, 'p2g_top': self.output_top_path}
