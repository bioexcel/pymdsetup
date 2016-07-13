# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS genion module

@author: pau
"""

import shutil
import tempfile
import os
try:
    import tools.file_utils as fu
    from command_wrapper import cmd_wrapper
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.tools import file_utils as fu
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.dummies_pycompss.task import task
    from pymdsetup.dummies_pycompss.constraint import constraint
    from pymdsetup.dummies_pycompss.parameter import *


class Genion512(object):
    """Wrapper for the 5.1.2 version of the genion module
    """

    def __init__(self, tpr_path, output_gro_path, input_top, output_top,
                 replaced_group="SOL", neutral=False, concentration=0.05,
                 seed='None', log_path='None',
                 error_path='None', gmx_path='None'):
        self.tpr_path = tpr_path
        self.output_gro_path = output_gro_path
        self.input_top = input_top
        self.output_top = output_top
        self.replaced_group = replaced_group
        self.neutral = neutral
        self.concentration = concentration
        self.seed = seed
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        shutil.copy(self.input_top, self.output_top)
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = ["echo", self.replaced_group, "|", gmx, "genion", "-s",
               self.tpr_path, "-o", self.output_gro_path,
               "-p", self.output_top]

        if self.neutral:
            cmd.append('-neutral')
        elif self.concentration:
            cmd.append('-conc')
            cmd.append(str(self.concentration))

        if self.seed != 'None':
            cmd.append('-seed')
            cmd.append(str(self.seed))

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

    @task(returns=dict, topin=FILE_IN, topout=FILE_OUT)
    def launchPyCOMPSs(self, top, tpr, topin, topout, itp_path, curr_path):
        fu.copy_ext(itp_path, curr_path, 'itp')
        shutil.copy(topin, topout)
        tempdir = tempfile.mkdtemp()
        temptop = os.path.join(tempdir, "gio.top")
        shutil.copy(topout, temptop)

        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = ["echo", self.replaced_group, "|", gmx, "genion", "-s",
               self.tpr_path, "-o", self.output_gro_path,
               "-p", temptop, "-neutral"]

        if self.seed != 'None':
            cmd.append('-seed')
            cmd.append(str(self.seed))

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        shutil.copy(temptop, topout)
        shutil.rmtree(tempdir)
        return {'gio_gro': self.output_gro_path, 'gio_top': self.output_top}
