#!/usr/bin/env python

"""Python wrapper module for the GROMACS solvate module
"""
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Solvate(object):
    """Wrapper for the 5.1.2 version of the GROMACS solvate module
    Args:
        input_solute_gro_path (str): Path to the input GRO file.
        output_gro_path (str): Path to the output GRO file.
        input_top_zip_path (str): Path the input TOP topology in zip format.
        output_top_zip_path (str): Path the output topology in zip format.
        properties (dic):
            output_top_path (str): Path the output TOP file.
            intput_solvent_gro_path (str): Path to the GRO file contanining the
                                           structure of the solvent.
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_solute_gro_path, output_gro_path,
                 input_top_zip_path, output_top_zip_path, properties, **kwargs):

        self.input_solute_gro_path = input_solute_gro_path
        self.output_gro_path = output_gro_path
        self.input_top_zip_path = input_top_zip_path
        self.output_top_zip_path = output_top_zip_path
        self.output_top_path = properties.get('output_top_path','sol.top')
        self.input_solvent_gro_path = properties.get('input_solvent_gro_path','spc216.gro')
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)

    def launch(self):
        """Launches the execution of the GROMACS solvate module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        self.output_top_path = fu.add_step_mutation_path_to_name(self.output_top_path, self.step, self.mutation)

        # Unzip topology to topology_out
        out_log.info('Before unzip')
        top_path = fu.unzip_top(zip_file=self.input_top_zip_path, top_file=self.output_top_path, out_log=out_log, dest_dir=self.mutation+'_'+self.step+'_top')
        out_log.info('After unzip')
        out_log.info(top_path)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'solvate',
               '-cp', self.input_solute_gro_path,
               '-cs', self.input_solvent_gro_path,
               '-o',  self.output_gro_path,
               '-p',  top_path]

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        out_log.info(cmd)
        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        returncode = command.launch()

        with open(top_path) as topology_file:
            out_log.info('Last 5 lines of new top file: ')
            lines = topology_file.readlines()
            for index in [-i for i in range(5,0,-1)]:
                out_log.info(lines[index])


        # zip new_topology
        fu.zip_top(top_path, self.output_top_zip_path, remove_files=False, mutation=self.mutation, out_log=out_log)
        return returncode

#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Solvate(input_solute_gro_path=sys.argv[4],
            output_gro_path=sys.argv[5],
            input_top_zip_path=sys.argv[6],
            output_top_zip_path=sys.argv[7],
            properties=prop).launch()

if __name__ == '__main__':
    main()
