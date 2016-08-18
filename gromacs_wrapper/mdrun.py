"""Python wrapper for the GROMACS mdrun module
"""
import os.path as op

try:
    from command_wrapper import cmd_wrapper
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.dummies_pycompss.task import task
    from pymdsetup.dummies_pycompss.constraint import constraint
    from pymdsetup.dummies_pycompss.parameter import *


@task(returns=int)
def reduceMDR(a, b):
    """ Returns (a+b)/2
    """
    return (a+b)/2


def mergeReduce(function, data):
    """ Apply function cumulatively to the items of data,
        from left to right in binary tree structure, so as to
        reduce the data to a single value.
    Args:
        function: function to apply to reduce data
        data (:obj:`list`): List of items to be reduced

    Returns:
        :obj: Result of reduce the data to a single value
    """
    from collections import deque
    q = deque(xrange(len(data)))
    while len(q):
        x = q.popleft()
        if len(q):
            y = q.popleft()
            data[x] = function(data[x], data[y])
            q.append(x)
        else:
            return data[x]


class Mdrun512(object):
    """Wrapper for the 5.1.2 version of the mdrun module
    Args:
        tpr_path (str): Path to the portable binary run input file TPR.
        output_trr_path (str): Path to the GROMACS uncompressed raw trajectory
                               file TRR.
        output_gro_path (str): Path to the output GROMACS structure GRO file.
        output_edr_path (str): Path to the output GROMACS portable energy file
                               EDR.
        output_xtc_path (str): Path to the GROMACS compressed trajectory file
                               XTC.
        output_cpt_path (str): Path to the output GROMACS checkpoint file CPT.
        log_path (str): Path to the file where the mdrun log will be stored.
        error_path (str): Path to the file where the mdrun error log will be
                          stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, tpr_path, output_trr_path, output_gro_path,
                 output_edr_path, output_xtc_path='None',
                 output_cpt_path='None', log_path='None',
                 error_path='None', gmx_path='None'):
        self.tpr_path = tpr_path
        self.output_gro_path = output_gro_path
        self.output_trr_path = output_trr_path
        self.output_edr_path = output_edr_path
        self.output_xtc_path = output_xtc_path
        self.output_cpt_path = output_cpt_path
        self.gmx_path = gmx_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        """Launches the execution of the GROMACS mdrun module.
        """
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "mdrun", "-s", self.tpr_path, "-o", self.output_trr_path,
               "-c", self.output_gro_path, "-e", self.output_edr_path]
        if not self.output_xtc_path == 'None':
            cmd.append("-x")
            cmd.append(self.output_xtc_path)
        if not self.output_cpt_path == 'None':
            cmd.append("-cpo")
            cmd.append(self.output_cpt_path)

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        command.move_file_output("md.log", op.dirname(self.output_trr_path))

    @task(returns=dict)
    def launchPyCOMPSs(self, tpr):
        """Launches the GROMACS mdrun module using the PyCOMPSs library.
        Args:
            tpr (str): Path to the portable binary run input file TPR.
        """
        self.launch()
        return {'md_gro': self.output_gro_path, 'md_trr': self.output_trr_path,
                'md_edr': self.output_edr_path, 'md_cpt': self.output_cpt_path}

    @classmethod
    def mergeResults(cls, mdrunList):
        result = mergeReduce(reduceMDR, mdrunList)
        return result
