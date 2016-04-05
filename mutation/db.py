"""Mutation fetcher module

"""
import requests
import re


class MMBVariants(object):
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
        variants = requests.get(url_uniprot_mut).json()['variants.vardata.mut']
        pattern = re.compile(("p.(?P<wt>[a-zA-Z]{3})"
                              "(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))
        return [pattern.match(var).groupdict() for var in variants]
