import requests
import os
import shutil
import json
import gzip
from mmb_api import pdb

class Dude(object):
    """Wrapper class for DUDE decoys database.
    This class is a wrapper for the DUDE database (http://dude.docking.org)

    """
    def __init__(self, url=None):
        self.url = url if url else "http://dude.docking.org"
        self.targets = {
            "3eml":"AA2AR", "2hzi":"ABL1",  "3bkl":"ACE",   "1e66":"ACES",  "2e1w":"ADA",
            "2oi0":"ADA17", "2vt4":"ADRB1", "3ny8":"ADRB2", "3cqw":"AKT1",  "3d0e":"AKT2",
            "2hv5":"ALDR",  "1l2s":"AMPC",  "2am9":"ANDR",  "1s3b":"AOFB",  "3l5d":"BACE1",
            "3d4q":"BRAF",  "1bcd":"CAH2",  "2cnk":"CASP3", "1h00":"CDK2",  "3bwm":"COMT",
            "1r9o":"CP2C9", "3nxu":"CP3A4", "3krj":"CSF1R", "3odu":"CXCR4", "1lru":"DEF",
            "3frj":"DHI1",  "2i78":"DPP4",  "3pbl":"DRD3",  "3nxo":"DYR",   "2rgp":"EGFR",
            "1sj0":"ESR1",  "2fsz":"ESR2",  "3kl6":"FA10",  "1w7x":"FA7",   "2nnq":"FABP4",
            "3bz3":"FAK1",  "3c4f":"FGFR1", "1j4h":"FKB1A", "3e37":"FNTA",  "1zw5":"FPPS",
            "3bqd":"GCR",   "2v3f":"GLCM",  "3kgc":"GRIA2", "1vso":"GRIK1", "1xl2":"HIVPR",
            "3lan":"HIVRT", "3ccw":"HMDH",  "1uyg":"HS90A", "3f9m":"HXK4",  "2oj9":"IGF1R",
            "2h7l":"INHA",  "2ica":"ITAL",  "3lpb":"JAK2",  "3cjo":"KIF11", "3g0e":"KIT",
            "2b8t":"KITH",  "2i0e":"KPCB",  "2of2":"LCK",   "3chp":"LKHA4", "3m2w":"MAPK2",
            "2aa2":"MCR",   "3lq8":"MET",   "2ojg":"MK01",  "2zdt":"MK10",  "2qd9":"MK14",
            "830c":"MMP13", "3eqh":"MP2K1", "1qw6":"NOS1",  "1b9v":"NRAM",  "1kvo":"PA2GA",
            "3l3m":"PARP1", "1udt":"PDE5A", "2oyu":"PGH1",  "3ln1":"PGH2",  "2owb":"PLK1",
            "3bgs":"PNPH",  "2p54":"PPARA", "2znp":"PPARD", "2gtk":"PPARG", "3kba":"PRGR",
            "2azr":"PTN1",  "1njs":"PUR2",  "1c8k":"PYGM",  "1d3g":"PYRD",  "3g6z":"RENI",
            "2etr":"ROCK1", "1mv9":"RXRA",  "1li4":"SAHH",  "3el8":"SRC",   "3hmm":"TGFR1",
            "1q4x":"THB",   "1ype":"THRB",  "2ayw":"TRY1",  "2zec":"TRYB1", "1syn":"TYSY",
            "1sqt":"UROK",  "2p2i":"VGFR2", "3biz":"WEE1",  "3hl5":"XIAP"}

    def get_decoys_from_pdb(self, pdb_code, output_sdf_path):
        """
        Returns the pdb_code decoys
        """
        if pdb_code in self.targets:
            target = self.targets.get(pdb_code.lower())
        else:
            pdb_set = pdb.MmbPdb().get_cluster_pdb_codes(pdb_code.lower())
            targets_set = set(self.targets.keys())
            targets_pdb_set = pdb_set.intersection(targets_set)
            target = self.targets.get(targets_pdb_set.pop()).lower()
            if not target:
                return None

        decoys_file_name = 'decoys_final.sdf.gz'
        url = self.url+'/targets/'+target.lower()+'/'+decoys_file_name
        req = requests.get(url, allow_redirects=True)
        with open(decoys_file_name, 'wb') as gz_file:
            gz_file.write(req.content)
        with gzip.open(decoys_file_name, 'rb') as gz_file:
            with open(output_sdf_path, 'wb') as sdf_file:
                sdf_file.write(gz_file.read())

        return output_sdf_path
