# -*- coding: utf-8 -*-
"""Unittests for structure.db module

@author: pau
"""
import unittest
from pymdsetup.structure.db import MMBStructure
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

    def test_get_pdb(self):
        pdb_code = '2ki5'
        output_path = opj(self.results, 'structure.pdb')
        gold_path = opj(self.data_dir, '2ki5_gold.pdb')
        mmb_st = MMBStructure(pdb_code, output_path)
        mmb_st.get_pdb()
        with open(output_path, 'r') as out_file, open(gold_path,
                                                      'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())


if __name__ == '__main__':
    unittest.main()
