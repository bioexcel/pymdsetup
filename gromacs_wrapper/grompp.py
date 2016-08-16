"""Python wrapper for the GROMACS grompp module
"""
import shutil
import os.path as op

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


class Grompp512(object):
    """Wrapper for the 5.1.2 version of the GROMACS grompp module.
    The GROMACS preprocessor module needs to be feeded with the input system
    and the molecular dynamics parameter file MDP, to create a portable binary
    run input file TPR.

    Args:
        mdp_path (str): Path to the input GROMACS parameter input file MDP.
        gro_path (str): Path to the input GROMACS structure GRO file.
        top_path (str): Path the input GROMACS topology TOP file.
        output_tpr_path (str): Path to the portable binary run input file TPR.
        cpt_path (str): Path to the GROMACS checkpoint file CPT.
        log_path (str): Path to the file where the pdb2gmx log will be stored.
        error_path (str): Path to the file where the pdb2gmx error log will be
                          stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, mdp_path, gro_path, top_path, output_tpr_path,
                 cpt_path='None', log_path='None', error_path='None',
                 gmx_path='None'):
        self.mdp_path = mdp_path
        self.gro_path = gro_path
        self.top_path = top_path
        self.output_tpr_path = output_tpr_path
        self.cpt_path = cpt_path
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        """Launches the execution of the GROMACS grompp module.
        """
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "grompp", "-f", self.mdp_path, "-c", self.gro_path, "-p",
               self.top_path, "-o", self.output_tpr_path]
        if self.cpt_path != 'None':
            cmd.append("-t")
            cmd.append(self.cpt_path)

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        command.move_file_output("mdout.mdp", op.dirname(self.output_tpr_path))

    @task(returns=dict)
    def launchPyCOMPSs(self, last_step, mdp_path):
        """Launches the GROMACS grompp module using the PyCOMPSs library.

        Args:
            last_step (dict): Output of the last PyCOMPSs step.
            mdp_path (str): Path to the input GROMACS parameter input file MDP.
        """
        #fu.copy_ext(itp_path, curr_path, 'itp')
        shutil.copy(mdp_path, self.mdp_path)
        self.launch()
        return {'gpp_tpr': self.output_tpr_path}
