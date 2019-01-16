#!/usr/bin/env python

"""Python wrapper module for the GROMACS editconf module
"""
import sys
import json
from command_wrapper import cmd_wrapper
import configuration.settings as settings
from tools import file_utils as fu

class Editconf(object):
    """Wrapper for the 5.1.2 version of the editconf module
    Args:
        input_gro_path (str): Path to the input GRO file.
        output_gro_path (str): Path to the output GRO file.
        properties (dic):
            distance_to_molecule (float): Distance of the box from the outermost
                                          atom in nm. ie 1.0nm = 10 Angstroms.
            box_type (str): Geometrical shape of the solvent box.
                            Available box types: octahedron, cubic, etc.
            center_molecule (bool): Center molecule in the box.
    """

    def __init__(self, input_gro_path, output_gro_path, properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_gro_path = input_gro_path
        self.output_gro_path = output_gro_path
        self.distance_to_molecule = properties.get('distance_to_molecule',1.0)
        self.box_type = properties.get('box_type', 'cubic')
        self.center_molecule = properties.get('center_molecule',False)
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)

    def launch(self):
        """Launches the execution of the GROMACS editconf module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'editconf', '-f', self.input_gro_path,
               '-o', self.output_gro_path,
               '-d', str(self.distance_to_molecule),
               '-bt', self.box_type]

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        if self.center_molecule:
            cmd.append('-c')

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        return command.launch()

#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Editconf(input_gro_path=sys.argv[4],
             output_gro_path=sys.argv[5],
             properties=prop).launch()

if __name__ == '__main__':
    main()
