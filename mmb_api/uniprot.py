"""Mutation fetcher module

"""
import requests
import re


class MmbVariants(object):
    """
    """

    def __init__(self, pdb_code):
        self.pdb_code = pdb_code.lower()
        self.uniprot = self.get_uniprot()

    def get_uniprot(self):
        url_uniprot_id = ("http://mmb.irbbarcelona.org"
                          "/api/pdb/"+self.pdb_code.lower()+"/entry"
                          "/uniprotRefs/_id")
        return requests.get(url_uniprot_id).json()['uniprotRefs._id'][0]

    def get_variants(self):
        url_uniprot_mut = ("http://mmb.irbbarcelona.org"
                           "/api/uniprot/"+self.uniprot+"/entry"
                           "/variants/vardata/mut/?varorig=humsavar")
        return requests.get(url_uniprot_mut).json()['variants.vardata.mut']

    def get_pdb_variants(self):
        url_mapPDBRes = ("http://mmb.irbbarcelona.org/api/"
                         "uniprot/"+self.uniprot+"/mapPDBRes?pdbId="
                         + self.pdb_code)

        pattern = re.compile(("p.(?P<wt>[a-zA-Z]{3})"
                              "(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))

        unfiltered_dic = requests.get(url_mapPDBRes).json()
        if len(unfiltered_dic) == 0:
            return []

        mapdic = requests.get(url_mapPDBRes).json()
        mutations = []
        uniprot_var = self.get_variants()
        print "VARIANTS: " + str(uniprot_var)
        print ""
        for var in uniprot_var:
            print "VAR: " + var
            uni_mut = pattern.match(var).groupdict()
            for k in mapdic.keys():
                for fragment in mapdic[k]:
                    if int(fragment['unp_start']) <= int(uni_mut['resnum']) <= int(fragment['unp_end']):
                        resnum = int(uni_mut['resnum']) + int(fragment['pdb_start']) - int(fragment['unp_start'])
                        mutations.append(k[-1]+'.'+uni_mut['wt']+str(resnum)+uni_mut['mt'])
                        print str(fragment) + "<====== ACCEPTED"
                    else:
                        print str(fragment) + "<====== DENIED"
        return mutations
