#!/usr/bin/env python

"""Python wrapper for the GROMACS mdrun module
"""
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Mdrun(object):
    """Wrapper for the 5.1.2 version of the mdrun module
    Args:
        input_tpr_path (str): Path to the portable binary run input file TPR.
        output_trr_path (str): Path to the GROMACS uncompressed raw trajectory file TRR.
        output_gro_path (str): Path to the output GROMACS structure GRO file.
        properties (dic):
            output_edr_path (str): Path to the output GROMACS portable energy file EDR.
            output_xtc_path (str): Path to the GROMACS compressed trajectory file XTC.
            num_threads (str): The number of threads that is going to be used.
            gmx_path (str): Path to the GROMACS executable binary.
        output_cpt_path (str): Path to the output GROMACS checkpoint file CPT.
    """

    def __init__(self, input_tpr_path, output_gro_path, properties,
                 output_trr_path=None, output_cpt_path=None,
                 output_xtc_path=None, output_edr_path=None,
                 output_log_path=None, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_tpr_path = input_tpr_path
        self.output_trr_path = output_trr_path
        self.output_gro_path = output_gro_path
        self.output_cpt_path = output_cpt_path
        self.output_xtc_path = output_xtc_path
        self.output_edr_path = output_edr_path
        self.output_log_path = output_log_path
        self.num_threads = properties.get('num_threads',None)
        self.ntmpi = properties.get('ntmpi', None)
        self.ntomp = properties.get('ntomp', None)
        self.gpu_id = properties.get('gpu_id', None)
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)
        self.mpirun_ppn = properties.get('mpirun_ppn', None)

    def launch(self):
        """Launches the execution of the GROMACS mdrun module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
	if self.mpirun is not None:
	    gmx = 'gmx'
        cmd = [gmx, 'mdrun', '-s', self.input_tpr_path, '-c', self.output_gro_path]

        if self.output_trr_path is not None:
            cmd.append('-o')
            cmd.append(self.output_trr_path)
        if self.output_xtc_path is not None:
            cmd.append('-x')
            cmd.append(self.output_xtc_path)
        if self.output_edr_path is not None:
            cmd.append('-e')
            cmd.append(self.output_edr_path)
        if self.output_cpt_path is not None:
            cmd.append('-cpo')
            cmd.append(self.output_cpt_path)
        if self.output_log_path is not None:
            cmd.append('-g')
            cmd.append(self.output_log_path)

	if self.mpirun_ppn is not None:
            cmd.insert(0, str(self.mpirun_ppn))
            cmd.insert(0, '-ppn')

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        #Number of threads to run (0 is guess)
        if not self.num_threads is None:
            cmd.append('-nt')
            cmd.append(str(self.num_threads))
        if not self.ntmpi is None:
            cmd.append('-ntmpi')
            cmd.append(str(self.ntmpi))
        if not self.ntomp is None:
            cmd.append('-ntomp')
            cmd.append(str(self.ntomp))
        if not self.gpu_id is None:
            cmd.append('-gpu_id')
            cmd.append(str(self.gpu_id))

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        return command.launch()

#Creating a main function to be compatible with CWL
def main():
    if len(sys.argv) < 8:
        sys.argv.append(None)
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Mdrun(input_tpr_path = sys.argv[4],
          output_trr_path = sys.argv[5],
          output_gro_path = sys.argv[6],
          output_cpt_path = sys.argv[7],
          properties=prop).launch()

if __name__ == '__main__':
    main()
