# -*- coding: utf-8 -*-
"""Python wrapper for the GROMACS editconf module

@author: pau
"""
try:
    import tools.file_utils as fu
    from command_wrapper import cmd_wrapper
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.task import task
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.tools import file_utils as fu
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.dummies_pycompss.task import task
    from pymdsetup.dummies_pycompss.constraint import constraint
    from pymdsetup.dummies_pycompss.parameter import *


class Editconf512(object):
    """Wrapper for the 5.1.2 version of the editconf module
    """

    def __init__(self, structure_gro_path, output_gro_path,
                 distance_to_molecule=1.0, box_type='octahedron',
                 center_molecule=True, log_path='None', error_path='None',
                 gmx_path='None'):
        self.structure_gro_path = structure_gro_path
        self.output_gro_path = output_gro_path
        self.distance_to_molecule = distance_to_molecule
        self.box_type = box_type
        self.center_molecule = center_molecule
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "editconf", "-f", self.structure_gro_path,
               "-o", self.output_gro_path, "-d",
               str(self.distance_to_molecule), "-bt", self.box_type]
        if self.center_molecule:
            cmd.append("-c")

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

    @task(returns=str)
    def launchPyCOMPSs(self, gro_path):
        self.launch()
        return self.output_gro_path
