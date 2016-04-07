"""Mutation fetcher module

"""
import requests


class MmbVariants(object):
    """
    """

    def __init__(self, pdb_code):
        self.pdb_code = pdb_code

    def fetch_variants(self):
        url_uniprot_id = ("http://mmb.irbbarcelona.org"
                          "/api/pdb/"+self.pdb_code.lower()+"/entry"
                          "/uniprotRefs/_id")
        uniprot_id = requests.get(url_uniprot_id).json()['uniprotRefs._id'][0]
        url_uniprot_mut = ("http://mmb.irbbarcelona.org"
                           "/api/uniprot/"+str(uniprot_id)+"/entry"
                           "/variants/vardata/mut/")
        return requests.get(url_uniprot_mut).json()['variants.vardata.mut']
