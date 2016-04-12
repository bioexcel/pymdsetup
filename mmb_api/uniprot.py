"""Mutation fetcher module

"""
import requests


class MmbVariants(object):
    """
    """

    def __init__(self, pdb_code):
        self.pdb_code = pdb_code

    def get_uniprot(self):
        url_uniprot_id = ("http://mmb.irbbarcelona.org"
                          "/api/pdb/"+self.pdb_code.lower()+"/entry"
                          "/uniprotRefs/_id")
        return requests.get(url_uniprot_id).json()['uniprotRefs._id'][0]

    def fetch_variants(self):
        url_uniprot_mut = ("http://mmb.irbbarcelona.org"
                           "/api/uniprot/"+self.get_uniprot()+"/entry"
                           "/variants/vardata/mut/")
        return requests.get(url_uniprot_mut).json()['variants.vardata.mut']
