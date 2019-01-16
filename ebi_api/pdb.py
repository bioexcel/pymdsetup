import requests
import os
import shutil
import itertools


class EbiPdb(object):
    """EBI PDBe entry downloader.

    This class is used to download PDB files from the european PDB repository
    (http://www.ebi.ac.uk/pdbe)
    """

    def __init__(self, url=None):
        self.url = url if url else "http://www.ebi.ac.uk/pdbe/entry-files/"

    def get_pdb(self, pdb_code, output_pdb_path):
        """
        Writes the PDB file content of `self._pdb_code`
        to `self._output_pdb_path`
        """
        if os.path.isfile(pdb_code):
            shutil.copy(pdb_code, output_pdb_path)
        else:
            url = (self.url+"pdb"+pdb_code.lower()+".ent")
            pdb_string = requests.get(url).content
            lines = pdb_string.splitlines(True)

            with open(output_pdb_path, 'w') as pdb_file:
                pdb_file.write(''.join(itertools.dropwhile(
                               lambda line: line[:6] != "ATOM  ", lines)))
