#!/usr/bin/env python

"""Python wrapper module for the GROMACS pdb2gmx module
"""
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Pdb2gmx(object):
    """Wrapper class for the 5.1.2 version of the GROMACS pdb2gmx module.
    Args:
        input_structure_pdb_path (str): Path to the input PDB file.
        output_gro_path (str): Path to the output GRO file.
        output_top_zip_path (str): Path the output TOP topology in zip format.
        properties (dic):
            output_top_path (str): Path the output TOP file.
            output_itp_path (str): Path the output itp file.
            water_type (str): Water molecule type.
                Valid values: tip3p, spce, etc.
            force_field (str): Force field to be used during the conversion.
                Valid values: amber99sb-ildn, oplsaa, etc.
            ignh (bool): Should pdb2gmx ignore the hidrogens in the original
                structure.
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_structure_pdb_path, output_gro_path,
                 output_top_zip_path, properties, **kwargs):

        self.input_structure_pdb_path = input_structure_pdb_path
        self.output_gro_path = output_gro_path
        self.output_top_zip_path = output_top_zip_path
        self.output_top_path = properties.get('output_top_path','p2g.top')
        self.output_itp_path = properties.get('output_itp_path',None)
        self.water_type = properties.get('water_type','spce')
        self.force_field = properties.get('force_field','amber99sb-ildn')
        self.ignh = properties.get('ignh',False)
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun',False)
        self.mpirun_np = properties.get('mpirun_np',None)


    def launch(self):
        """Launches the execution of the GROMACS pdb2gmx module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        self.output_top_path = fu.add_step_mutation_path_to_name(self.output_top_path, self.step, self.mutation)

        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = [gmx, "pdb2gmx", "-f", self.input_structure_pdb_path,
               "-o", self.output_gro_path, "-p", self.output_top_path,
               "-water", self.water_type, "-ff", self.force_field]

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        if self.output_itp_path is not None:
            self.output_itp_path = self.output_itp_path if self.step is None else self.step+'_'+self.output_itp_path
            self.output_itp_path = self.output_itp_path if self.mutation is None else self.mutation+'_'+self.output_itp_path
            cmd.append("-i")
            cmd.append(self.output_itp_path)
        if self.ignh:
            cmd.append("-ignh")

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        returncode = command.launch()

        #Remove comment (first line) from gro file
        with open(self.output_gro_path, 'r') as fin:
            data = fin.read().splitlines(True)
            data[0] = 'Created with pdb2gmx building block\n'
        with open(self.output_gro_path, 'w') as fout:
            fout.writelines(data)

        # zip topology
        fu.zip_top(self.output_top_path, self.output_top_zip_path, remove_files=False, mutation=self.mutation, out_log=out_log)

        return returncode
#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Pdb2gmx(input_structure_pdb_path=sys.argv[4],
            output_gro_path=sys.argv[5],
            output_top_zip_path=sys.argv[6],
            properties=prop).launch()

if __name__ == '__main__':
    main()
