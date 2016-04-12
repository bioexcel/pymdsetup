"""

"""
import re
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB import PDBIO
from pymdsetup.command_wrapper import cmd_wrapper

try:
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.task import task
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.pycompss_dummies.task import task
    from pymdsetup.pycompss_dummies.constraint import constraint
    from pymdsetup.pycompss_dummies.parameter import *


class Scwrl4(object):
    """
    """

    def __init__(self, pdb_path, output_pdb_path, mutation, log_path='None',
                 error_path='None', scwrl_path='None'):
        self.pdb_path = pdb_path
        self.output_pdb_path = output_pdb_path
        pattern = re.compile(("p.(?P<wt>[a-zA-Z]{3})"
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
        residue = st[0]['A'][(' ', int(self.mutation['resnum']), ' ')]
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

    @task(returns=dict)
    def launchPyCOMPSs(self):
        self.launch()
        return {'scw_pdb': self.output_pdb_path}
