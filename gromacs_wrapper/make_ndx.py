#!/usr/bin/env python

"""Python wrapper module for the GROMACS make_ndx module
"""
import sys
import json
import re
from command_wrapper import cmd_wrapper
import configuration.settings as settings
from tools import file_utils as fu


class MakeNdx(object):
    """Wrapper for the 5.1.2 version of the make_ndx module
    Args:
        input_structure_path (str): Path to the input GRO/PDB/TPR file.
        output_ndx_path (str): Path to the output index NDX file.
        properties (dic):
            selection (str): Atom selection string.
    """

    def __init__(self, input_structure_path, output_ndx_path, properties, **kwargs):

        self.input_structure_path = input_structure_path
        self.output_ndx_path = output_ndx_path
        self.selection = properties.get('selection', None)
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
        cmd = [gmx, 'make_ndx', '-f', self.input_structure_path,
               '-o', self.output_ndx_path]

        pattern = re.compile(("(?P<chain>[a-zA-Z*]+).(?P<wt>[a-zA-Z]{3})(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))
        self.mut_dict = pattern.match(self.mutation).groupdict()

        out_log.info("")
        out_log.info("Old selection: ")
        out_log.info(self.selection)
        out_log.info("")

        self.selection = self.selection.replace("RES_NUM", self.mut_dict['resnum'])

        out_log.info("")
        out_log.info("New selection: ")
        out_log.info(self.selection)
        out_log.info("")


        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')

        if self.mpirun:
            cmd.append('<<<')
            cmd.append('\"'+self.selection+'\"')
        else:
            cmd.insert(0, '|')
            cmd.insert(0, '\"'+self.selection+'\"')
            cmd.insert(0, '-e')
            cmd.insert(0, 'echo')

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        return command.launch()

#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    MakeNdx(input_structure_path=sys.argv[4],
             output_ndx_path=sys.argv[5],
             properties=prop).launch()

if __name__ == '__main__':
    main()
