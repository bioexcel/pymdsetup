"""Python wrapper module for SCWRL
"""
import re
import os
from os.path import join as opj
import shutil
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB import PDBIO

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


class Scwrl4(object):
    """Wrapper class for the 4.0 version of SCWRL.

    Args:

    """

    def __init__(self, pdb_path, output_pdb_path, mutation, log_path='None',
                 error_path='None', scwrl_path='None'):
        self.pdb_path = pdb_path
        self.output_pdb_path = output_pdb_path
        pattern = re.compile(("(?P<chain>[a-zA-Z]{1}).(?P<wt>[a-zA-Z]{3})"
                              "(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))
        self.mutation = pattern.match(mutation).groupdict()
        self.scwrl_path = scwrl_path
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        # Read structure with Biopython
        parser = PDBParser(PERMISSIVE=1)
        st = parser.get_structure('s', self.pdb_path)  # s random id never used

        # Remove the side chain of the AA to be mutated
        chain = self.mutation['chain']
        resnum = int(self.mutation['resnum'])
        residue = st[0][chain][(' ', resnum, ' ')]
        backbone_atoms = ['N', 'CA', 'C', 'O', 'CB']
        not_backbone_atoms = []
        '''
        The following formula does not work. Biopython bug?
        for atom in residue:
            if atom.id not in backbone_atoms:
                residue.detach_child(atom.id)
        '''
        for atom in residue:
            if atom.id not in backbone_atoms:
                not_backbone_atoms.append(atom)
        for atom in not_backbone_atoms:
            residue.detach_child(atom.id)

        # Change residue name
        residue.resname = self.mutation['mt'].upper()

        # Write resultant structure
        w = PDBIO()
        w.set_structure(st)
        prepared_file_path = self.output_pdb_path + '.scwrl4.prepared.pdb'
        w.save(prepared_file_path)

        scrwl = "Scwrl4" if self.scwrl_path == 'None' else self.scwrl_path
        cmd = [scrwl, "-i", prepared_file_path, "-o", self.output_pdb_path]

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

        # Move hot.grp file
        f = 'hot.grp'
        if os.path.exists(f):
            shutil.move(f, opj(os.path.dirname(self.output_pdb_path), f))

    @task(returns=str)
    def launchPyCOMPSs(self):
        """ Launches SCWRL 4 using the PyCOMPSs library.
        """
        self.launch()
        return self.output_pdb_path
