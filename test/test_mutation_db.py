"""Unittests for mutation.db module

@author: pau
"""
import unittest
from pymdsetup.mutation.db import MMBVariants
import os
from os.path import join as opj


class TestMMBStructure(unittest.TestCase):

    def setUp(self):
        self.data_dir = opj(os.path.dirname(__file__), 'data')
        self.results = opj(self.data_dir, "temp_results")

    def tearDown(self):
        # Remove all files in the temp_results directory
        for the_file in os.listdir(self.results):
            file_path = opj(self.results, the_file)
            try:
                # Not removing directories
                if os.path.isfile(file_path) and not the_file == 'README.txt':
                    os.unlink(file_path)
            except Exception, e:
                print e

    def test_fetch_variants(self):
        pdb_code = '3vtv'
        mmb_st = MMBVariants(pdb_code)
        variants = mmb_st.fetch_variants()
        variants_expected = [{'mt': u'Asp', 'wt': u'His', 'resnum': u'26'},
                             {'mt': u'Lys', 'wt': u'Glu', 'resnum': u'50'}]
        self.assertEqual(variants[:2], variants_expected)


if __name__ == '__main__':
    unittest.main()
