"""Mutation modeler

"""
import requests
import os
import shutil


class MmbPdb(object):
    """
    """

    def __init__(self, pdb_code, output_pdb_path):
        self.pdb_code = pdb_code
        self.output_pdb_path = output_pdb_path
        self.filter = "filter=/1&group=ATOM"

    def get_pdb(self):
        if os.path.isfile(self.pdb_code):
            shutil.copy(self.pdb_code, self.output_pdb_path)
        else:
            url = ("http://mmb.irbbarcelona.org"
                   "/api/pdb/"+self.pdb_code.lower()+"/coords/?"+self.filter)
            pdb_string = requests.get(url).content
            with open(self.output_pdb_path, 'w') as pdb_file:
                pdb_file.write(pdb_string)
