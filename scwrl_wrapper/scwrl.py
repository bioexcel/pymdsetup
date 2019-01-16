#!/usr/bin/env python

"""Python wrapper module for SCWRL
"""
import sys
import re
import json
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB import PDBIO
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Scwrl4(object):
    """Wrapper class for the 4.0 version of SCWRL.
    Args:
        input_pdb_path (str): Path to the input PDB file.
        output_pdb_path (srt): Path to the output mutated PDB file.
        properties (dic): All properties and system path
    """
    def __init__(self, input_pdb_path, output_pdb_path, properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_pdb_path = input_pdb_path
        self.output_pdb_path = output_pdb_path
        self.scwrl4_path = properties.get('scwrl4_path',None)
        self.path = properties.get('path','')
        self.step = properties.get('step','')
        self.mutation = properties['mut'] if properties.get('mut', None) else properties['mutation']
        pattern = re.compile(("(?P<chain>[a-zA-Z*]+).(?P<wt>[a-zA-Z]{3})(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))
        self.mut_dict = pattern.match(self.mutation).groupdict()

    def launch(self):
        """Launches the execution of the SCWRL binary.
        """

        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        if self.mutation is not None:
            # Read structure with Biopython
            parser = PDBParser(PERMISSIVE=1,QUIET=True)
            st = parser.get_structure('s', self.input_pdb_path)  # s random id never used

            if self.mut_dict['chain'] != 'ALL':
                chains = [self.mut_dict['chain']]
            else:
                chains = [chain.id for chain in st[0]]

            resnum = int(self.mut_dict['resnum'])

            sequence=''
            for chain in chains:
                residue = st[0][chain][(' ', resnum, ' ')]
                backbone_atoms = ['N', 'CA', 'C', 'O', 'CB']
                not_backbone_atoms = []

                # The following formula does not work. Biopython bug?
                # for atom in residue:
                #     if atom.id not in backbone_atoms:
                #         residue.detach_child(atom.id)

                for atom in residue:
                    if atom.id not in backbone_atoms:
                        not_backbone_atoms.append(atom)
                for atom in not_backbone_atoms:
                    residue.detach_child(atom.id)

                # Change residue name
                residue.resname = self.mut_dict['mt'].upper()

                # Creating a sequence file where the lower case residues will
                # remain untouched and the upper case residues will be modified
                aa1c = { 'ALA':'A', 'CYS':'C', 'CYX':'C', 'ASP':'D', 'ASH':'D', 'GLU':'E', 'GLH':'E', 'PHE':'F', 'GLY':'G', 'HIS':'H', 'HID':'H', 'HIE':'H', 'HIP':'H', 'ILE':'I', 'LYS':'K', 'LYP':'K', 'LEU':'L', 'MET':'M', 'MSE':'M', 'ASN':'N', 'PRO':'P', 'HYP':'P', 'GLN':'Q', 'ARG':'R', 'SER':'S', 'THR':'T', 'VAL':'V', 'TRP':'W', 'TYR':'Y'}
                for res in st[0][chain].get_residues():
                    if res.resname not in aa1c:
                        st[0][chain].detach_child(res.id)
                    elif (res.id == (' ', resnum,' ')):
                        sequence += aa1c[res.resname].upper()
                    else:
                        sequence += aa1c[res.resname].lower()

            # Write resultant sequence
            sequence_file_path = fu.add_step_mutation_path_to_name("sequence.seq", self.step, self.mutation)
            with open(sequence_file_path, 'w') as sqfile:
                sqfile.write(sequence+"\n")

            # Write resultant structure
            w = PDBIO()
            w.set_structure(st)
            prepared_file_path = fu.add_step_mutation_path_to_name("prepared.pdb", self.step, self.mutation)
            w.save(prepared_file_path)

        else:
            prepared_file_path = self.input_pdb_path

        scrwl = 'Scwrl4' if self.scwrl4_path is None else self.scwrl4_path
        cmd = [scrwl, '-i', prepared_file_path, '-o', self.output_pdb_path, '-h', '-t']
        if self.mutation:
            cmd.append('-s')
            cmd.append(sequence_file_path)

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        return command.launch()

#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Scwrl4(input_pdb_path=sys.argv[4], output_pdb_path=sys.argv[5], properties=prop).launch()

if __name__ == '__main__':
    main()
