"""Mutation modeler

"""
import requests


class MMBStructure(object):
    """
    """

    def __init__(self, pdb_code, output_pdb_path):
        self.pdb_code = pdb_code
        self.output_pdb_path = output_pdb_path
        self.filter = "filter=/1&group=ATOM"

    def get_pdb(self):
        url = ("http://mmb.irbbarcelona.org"
               "/api/pdb/"+self.pdb_code.lower()+"/coords/?"+self.filter)
        print url
        pdb_string = requests.get(url).content
        with open(self.output_pdb_path, 'w') as pdb_file:
            pdb_file.write(pdb_string)
