# -*- coding: utf-8 -*-
"""Unittests for gromacs_wrapper.grompp module

@author: pau
"""
import unittest
from pymdsetup.gromacs_wrapper.grompp import Grompp512
import os
from os.path import join as opj
import filecmp


class TestGrompp512(unittest.TestCase):

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

        for the_file in os.listdir(os.getcwd()):
            file_path = opj(os.getcwd(), the_file)
            try:
                # Not removing directories
                if os.path.isfile(file_path) and the_file.startswith('#'):
                    os.unlink(file_path)
            except Exception, e:
                print e

    def test_launch_returns_correct_data(self):
        mdp_path = opj(self.data_dir, 'gmx_full_min.mdp')
        gro_path = opj(self.data_dir, 'genion512_gold.gro')
        top_path = opj(self.data_dir, 'genion512_gold.top')
        output_tpr_path = opj(self.results, 'grompp512_min.tpr')
        gold_tpr_path = opj(self.data_dir, 'grompp512_min_gold.tpr')

        gpp = Grompp512(mdp_path, gro_path, top_path, output_tpr_path)
        gpp.launch()

        self.assertTrue(filecmp.cmp(output_tpr_path, gold_tpr_path))

if __name__ == '__main__':
    unittest.main()
