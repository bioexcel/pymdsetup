# -*- coding: utf-8 -*-
"""Unittests for gromacs_wrapper.pdb2gmx module

@author: pau
"""
import unittest
from gromacs_wrapper.pdb2gmx import Pdb2gmx512
import os
from os.path import join as opj


class TestPdb2gmx512(unittest.TestCase):

    def setup(self):
        self.data_dir = opj(os.path.dirname(__file__), 'data')
        print self.data_dir
        self.results = opj(self.data_dir, "temp_results")

    def teardown(self):
        # Remove all files in the temp_results directory
        for the_file in os.listdir(self.results):
            file_path = opj(self.results, the_file)
            try:
                # Not removing directories
                if os.path.isfile(file_path) and the_file == 'readme.txt':
                    os.unlink(file_path)
            except Exception, e:
                print e

    def test_launch_returns_correct_data(self):
        pdb_path = opj(self.data_dir, '1NAG.pdb')
        output_gro_path = opj(self.results, '1NAG.gro')
        p2g = Pdb2gmx512(pdb_path, output_gro_path)
        p2g.launch()
        with open(output_gro_path, 'r') as out_gro, open('pdb2gmx512_gold.gro',
                                                         'r') as gold_gro:
            self.assertMultilineEqual(out_gro.read(), gold_gro.read())

if __name__ == '__main__':
    unittest.main()
