# -*- coding: utf-8 -*-
"""Unittests for gromacs_wrapper.solvate module

@author: pau
"""
import unittest
from pymdsetup.gromacs_wrapper.solvate import Solvate512
import os
from os.path import join as opj
import shutil


class TestSolvate512(unittest.TestCase):

    def setUp(self):
        self.data_dir = opj(os.path.dirname(__file__), 'data')
        self.results = opj(self.data_dir, "temp_results")

    # def tearDown(self):
    #     # Remove all files in the temp_results directory
    #     for the_file in os.listdir(self.results):
    #         file_path = opj(self.results, the_file)
    #         try:
    #             # Not removing directories
    #             if os.path.isfile(file_path) and not the_file == 'README.txt':
    #                 os.unlink(file_path)
    #         except Exception, e:
    #             print e
    #
    #     for the_file in os.listdir(os.getcwd()):
    #         file_path = opj(os.getcwd(), the_file)
    #         try:
    #             # Not removing directories
    #             if os.path.isfile(file_path) and the_file.startswith('#'):
    #                 os.unlink(file_path)
    #         except Exception, e:
    #             print e

    def test_launch_returns_correct_data(self):
        input_path = opj(self.data_dir, 'editconf512_gold.gro')
        shutil.copy(opj(self.data_dir, 'pdb2gmx512_gold.top'),
                    opj(self.results, 'solvate512.top'))
        top_path = opj(self.results, 'solvate512.top')
        gold_top_path = opj(self.data_dir, 'solvate512_gold.top')
        output_path = opj(self.results, 'solvate512.gro')
        gold_path = opj(self.data_dir, 'solvate512_gold.gro')
        p2g = Solvate512(input_path, output_path, top_path)
        p2g.launch()
        with open(output_path, 'r') as out_file, open(gold_path,
                                                      'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())

        with open(top_path, 'r') as out_top, open(gold_top_path,
                                                  'r') as gold_top:
            out_top_list = " ".join([line if not line.startswith(';')
                                    else '' for line in out_top])
            out_top_gold_list = " ".join([line if not line.startswith(';')
                                         else '' for line in gold_top])
            self.assertItemsEqual(out_top_list, out_top_gold_list)

if __name__ == '__main__':
    unittest.main()
