"""Python module for changing atom names using Biopython
"""

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
        pattern = re.compile(("(?P<chain>[a-zA-Z*]{1}).(?P<wt>[a-zA-Z]{3})(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))
        self.mut_dict = pattern.match(self.mutation).groupdict()
