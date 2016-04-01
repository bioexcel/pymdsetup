# -*- coding: utf-8 -*-
"""Unittests for gromacs_wrapper.pdb2gmx module

@author: pau
"""
import unittest
from pymdsetup.gromacs_wrapper.pdb2gmx import Pdb2gmx512
import os
from os.path import join as opj


class TestPdb2gmx512(unittest.TestCase):

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

    def test_launch_returns_correct_data(self):
        pdb_path = opj(self.data_dir, '1NAJ.pdb')
        output_gro_path = opj(self.results, 'pdb2gmx512.gro')
        output_top_path = opj(self.results, 'pdb2gmx512.top')
        gold_top_path = opj(self.data_dir, 'pdb2gmx512_gold.top')
        gold_gro_path = opj(self.data_dir, 'pdb2gmx512_gold.gro')
        p2g = Pdb2gmx512(pdb_path, output_gro_path, output_top_path)
        p2g.launch()

        with open(output_gro_path, 'r') as out_gro, open(gold_gro_path,
                                                         'r') as gold_gro:
            self.assertMultiLineEqual(out_gro.read(), gold_gro.read())

        with open(output_top_path, 'r') as out_top, open(gold_top_path,
                                                         'r') as gold_top:
            out_top_list = " ".join([line if not line.startswith(';')
                                    else '' for line in out_top])
            out_top_gold_list = " ".join([line if not line.startswith(';')
                                         else '' for line in gold_top])
            self.assertItemsEqual(out_top_list, out_top_gold_list)

if __name__ == '__main__':
    unittest.main()
