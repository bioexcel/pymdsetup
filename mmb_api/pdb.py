import requests
import os
import shutil


class MmbPdb(object):
    """Wrapper class for the MMB group PDB REST API.

    This class is a wrapper for the PDB (http://www.rcsb.org/pdb/home/home.do)
    mirror of the MMB group REST API (http://mmb.irbbarcelona.org/api/)

    Args:
        pdb_code (str): Protein Data Bank (PDB) four letter code.
            ie: '2ki5'
        output_pdb_path (str): File path where the PDB file will be stored.
            ie: '/home/user1/2ki5.pdb'
    """

    def __init__(self, pdb_code, output_pdb_path):
        self._pdb_code = pdb_code
        self._output_pdb_path = output_pdb_path
        self._filter = "filter=/1&group=ATOM"

    def get_pdb(self):
        """
        Writes the PDB file content of `self._pdb_code`
        to `self._output_pdb_path`
        """
        if os.path.isfile(self._pdb_code):
            shutil.copy(self._pdb_code, self._output_pdb_path)
        else:
            url = ("http://mmb.irbbarcelona.org"
                   "/api/pdb/"+self._pdb_code.lower()+"/coords/?"+self._filter)
            pdb_string = requests.get(url).content
            with open(self._output_pdb_path, 'w') as pdb_file:
                pdb_file.write(pdb_string)
