"""Mutation fetcher module
"""
import requests
import re


class MmbVariants(object):
    """Wrapper class for the MMB group UNIPROT REST API.
    This class is a wrapper for the UNIPROT (http://www.uniprot.org/)
    mirror of the MMB group REST API (http://mmb.irbbarcelona.org/api/)
    Args:
        pdb_code (str): Protein Data Bank (PDB) four letter code.
            ie: '2ki5'
    """
    def __init__(self, pdb_code):
        self._pdb_code = pdb_code.lower()
        self._uniprot = self.get_uniprot()
    def get_uniprot(self):
        """Returns the UNIPROT code corresponding to the `self._pdb_code`.

        Returns:
            str: UNIPROT code.
        """
        url_uniprot_id = ("http://mmb.irbbarcelona.org"
                          "/api/pdb/"+self._pdb_code.lower()+"/entry"
                          "/uniprotRefs/_id")
        return requests.get(url_uniprot_id).json()['uniprotRefs._id'][0]

    def get_variants(self):
        """Returns the variants of the `self._uniprot` code.

        Returns:
            :obj:`list` of :obj:`str`: List of variants
        """
        url_uniprot_mut = ("http://mmb.irbbarcelona.org"
                           "/api/uniprot/"+self._uniprot+"/entry"
                           "/variants/vardata/mut/?varorig=humsavar")
        variants = requests.get(url_uniprot_mut).json()['variants.vardata.mut']
        if variants is None:
            return []
        else:
            return variants

    def get_pdb_variants(self):
        """Returns the variants of the `self._uniprot` mapped to the
           `self_pdb`.

        Returns:
            :obj:`list` of :obj:`str`: List of mapped variants
        """
        url_mapPDBRes = ("http://mmb.irbbarcelona.org/api/"
                         "uniprot/"+self._uniprot+"/mapPDBRes?pdbId="
                         + self._pdb_code)

        pattern = re.compile(("p.(?P<wt>[a-zA-Z]{3})"
                              "(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))

        unfiltered_dic = requests.get(url_mapPDBRes).json()
        if len(unfiltered_dic) == 0:
            return []

        mapdic = requests.get(url_mapPDBRes).json()
        mutations = []
        uniprot_var = self.get_variants()
        if uniprot_var is None:
            return []
        for var in uniprot_var:
            # print "VAR: " + var
            uni_mut = pattern.match(var).groupdict()
            for k in mapdic.keys():
                for fragment in mapdic[k]:
                    if int(fragment['unp_start']) <= int(uni_mut['resnum']) <= int(fragment['unp_end']):
                        resnum = int(uni_mut['resnum']) + int(fragment['pdb_start']) - int(fragment['unp_start'])
                        mutations.append(k[-1]+'.'+uni_mut['wt']+str(resnum)+uni_mut['mt'])
                        # print str(fragment) + "<====== ACCEPTED"
                    else:
                        pass
                        # print str(fragment) + "<====== DENIED"
        return mutations
