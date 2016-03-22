# -*- coding: utf-8 -*-
"""Unittests for gromacs_wrapper.mdrun module

@author: pau
"""
import unittest
from pymdsetup.gromacs_wrapper.mdrun import Mdrun512
import os
from os.path import join as opj
import filecmp


class TestMdrun512(unittest.TestCase):

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
                if os.path.isfile(file_path) and the_file.startswith('#temp'):
                    os.unlink(file_path)
            except Exception, e:
                print e

    def test_launch_returns_correct_data(self):
        tpr_path = opj(self.data_dir, 'grompp512_min_gold.tpr')

        trr_path = opj(self.results, 'mdrun512.trr')
        gold_trr_path = opj(self.data_dir, 'mdrun512_gold.trr')
        gro_path = opj(self.results, 'mdrun512.gro')
        gold_gro_path = opj(self.data_dir, 'mdrun512_gold.gro')
        edr_path = opj(self.results, 'mdrun512.edr')
        gold_edr_path = opj(self.data_dir, 'mdrun512_gold.edr')
        mdr = Mdrun512(tpr_path, trr_path, gro_path, edr_path)
        mdr.launch()

        self.assertTrue(filecmp.cmp(trr_path, gold_trr_path))
        self.assertTrue(filecmp.cmp(gro_path, gold_gro_path))
        self.assertTrue(filecmp.cmp(edr_path, gold_edr_path))

if __name__ == '__main__':
    unittest.main()
