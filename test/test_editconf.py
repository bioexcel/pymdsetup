# -*- coding: utf-8 -*-
"""Unittests for gromacs_wrapper.editconf module

@author: pau
"""
import unittest
from gromacs_wrapper.editconf import Editconf512
import os
from os.path import join as opj


class TestEditconf512(unittest.TestCase):

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
        input_path = opj(self.data_dir, 'pdb2gmx512_gold.gro')
        output_path = opj(self.results, 'editconf512.gro')
        gold_path = opj(self.data_dir, 'editconf512_gold.gro')
        p2g = Editconf512(input_path, output_path)
        p2g.launch()
        with open(output_path, 'r') as out_file, open(gold_path,
                                                      'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())

if __name__ == '__main__':
    unittest.main()
