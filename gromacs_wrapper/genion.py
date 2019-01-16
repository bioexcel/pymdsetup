#!/usr/bin/env python

"""Python wrapper for the GROMACS genion module
"""
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Genion(object):
    """Wrapper for the 5.1.2 version of the genion module
    Args:
        input_tpr_path (str): Path to the input portable run input TPR file.
        output_gro_path (str): Path to the input structure GRO file.
        input_top_zip_path (str): Path the input TOP topology in zip format.
        output_top_zip_path (str): Path the output topology TOP and ITP files zipball.
        properties (dic):
            output_top_path (str): Path the output topology TOP file.
            replaced_group (str): Group of molecules that will be replaced by the solvent.
            neutral (bool): Neutralize the charge of the system.
            concentration (float): Concentration of the ions in (mol/liter).
            seed (int): Seed for random number generator.
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_tpr_path, output_gro_path, input_top_zip_path,
                 output_top_zip_path, properties, **kwargs):

        self.input_tpr_path = input_tpr_path
        self.output_gro_path = output_gro_path
        self.input_top_zip_path = input_top_zip_path
        self.output_top_zip_path = output_top_zip_path
        self.output_top_path = properties.get('output_top_path','gio.top')
        self.replaced_group = properties.get('replaced_group','SOL')
        self.neutral = properties.get('neutral',False)
        self.concentration = properties.get('concentration',0.05)
        self.seed = properties.get('seed',1993)
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)
        self.global_log= properties.get('global_log', None)

    def launch(self):
        """Launches the execution of the GROMACS genion module.
        """
        if self.global_log is not None:
            if self.concentration:
                self.global_log.info(22*' '+'To reach up '+str(self.concentration)+' mol/litre concentration')

        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        self.output_top_path = fu.add_step_mutation_path_to_name(self.output_top_path, self.step, self.mutation)

        # Unzip topology to topology_out
        top_path = fu.unzip_top(zip_file=self.input_top_zip_path, top_file=self.output_top_path, out_log=out_log, dest_dir=self.mutation+'_'+self.step+'_top')
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'genion',
               '-s', self.input_tpr_path,
               '-o', self.output_gro_path,
               '-p', top_path]

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        if self.neutral:
            cmd.append('-neutral')
        if self.concentration:
            cmd.append('-conc')
            cmd.append(str(self.concentration))

        if self.seed is not None:
            cmd.append('-seed')
            cmd.append(str(self.seed))

        if self.mpirun:
            cmd.append('<<<')
            cmd.append('\"'+self.replaced_group+'\"')
        else:
            cmd.insert(0, '|')
            cmd.insert(0, '\"'+self.replaced_group+'\"')
            cmd.insert(0, 'echo')
        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        returncode = command.launch()

        # zip new_topology
        fu.zip_top(top_path, self.output_top_zip_path, remove_files=False, mutation=self.mutation, out_log=out_log)
        return returncode

#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Genion(input_tpr_path = sys.argv[4],
           output_gro_path = sys.argv[5],
           input_top_zip_path = sys.argv[6],
           output_top_zip_path = sys.argv[7],
           properties=prop).launch()

if __name__ == '__main__':
    main()
