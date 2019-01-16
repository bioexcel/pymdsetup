#!/usr/bin/env python

"""Python wrapper for the GROMACS rms module
"""
import os
import sys
import json
import ntpath
import numpy as np
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Rms(object):
    """Wrapper for the 5.1.2 version of the rms module
    Args:
        input_gro_path (str): Path to the original (before launching the trajectory) GROMACS structure file GRO.
        input_xtc_paht (str): Path to the GROMACS compressed raw trajectory file XTC.
        output_xvg_path (str): Path to the simple xmgrace plot file XVG.
        properties (dic):
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_gro_path, input_trr_path, output_xvg_path,
                 properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_gro_path = input_gro_path
        self.input_xtc_path = input_xtc_path
        self.output_xvg_path = output_xvg_path
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)


    def launch(self):
        """Launches the execution of the GROMACS rms module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        gmx = 'gmx' if self.gmx_path is 'None' else self.gmx_path

        cmd = [gmx, 'rms', '-xvg', 'none',
               '-s', self.input_gro_path,
               '-f', self.input_xtc_path,
               '-o', self.output_xvg_path]

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
            cmd.append('<<<')
            cmd.append('\"'+"$'0\n0\n'"+'\"')
        else:
            cmd.insert(0, '|')
            cmd.insert(0, '\"'+'0 0'+'\"')
            cmd.insert(0, 'echo')
        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        command.launch()
        xvg = self.output_xvg_path if os.path.isfile(self.output_xvg_path) else ntpath.basename(self.output_xvg_path)
        self.mutation = '' if self.mutation is None else self.mutation
        return {self.mutation: np.loadtxt(xvg)}

#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Rms(input_gro_path=sys.argv[4],
        input_trr_path=sys.argv[5],
        output_xvg_path=sys.argv[6],
        properties=prop).launch()

if __name__ == '__main__':
    main()
