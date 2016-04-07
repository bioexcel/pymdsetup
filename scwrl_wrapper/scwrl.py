"""

"""
import re
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB import PDBIO


class Scwrl4(object):
    """
    """

    def __init__(self, pdb_path, output_pdb_path, mutation):
        self.pdb_path = pdb_path
        self.output_pdb_path = output_pdb_path
        pattern = re.compile(("p.(?P<wt>[a-zA-Z]{3})"
                              "(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))
        self.mutation = pattern.match(mutation).groupdict()

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
        w.save(self.output_pdb_path + '.scwrl4.prepared.pdb')
