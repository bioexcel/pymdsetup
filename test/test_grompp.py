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

    def test_launch_ions(self):
        mdp_path = opj(self.data_dir, 'gmx_full_ions.mdp')
        gro_path = opj(self.data_dir, 'solvate512_gold.gro')
        top_path = opj(self.data_dir, 'solvate512_gold.top')
        output_tpr_path = opj(self.results, 'grompp512_ions.tpr')
        gold_tpr_path = opj(self.data_dir, 'grompp512_ions_gold.tpr')
        output_log = opj(self.results, 'out.log')
        err_log = opj(self.results, 'err.log')

        gpp = Grompp512(mdp_path, gro_path, top_path, output_tpr_path,
                        log_path=output_log, error_path=err_log)
        gpp.launch()

        self.assertTrue(filecmp.cmp(output_tpr_path, gold_tpr_path))

    def test_launch_minimization(self):
        mdp_path = opj(self.data_dir, 'gmx_full_min.mdp')
        gro_path = opj(self.data_dir, 'genion512_gold.gro')
        top_path = opj(self.data_dir, 'genion512_gold.top')
        output_tpr_path = opj(self.results, 'grompp512_min.tpr')
        gold_tpr_path = opj(self.data_dir, 'grompp512_min_gold.tpr')

        gpp = Grompp512(mdp_path, gro_path, top_path, output_tpr_path)
        gpp.launch()

        self.assertTrue(filecmp.cmp(output_tpr_path, gold_tpr_path))

    def test_launch_nvt(self):
        mdp_path = opj(self.data_dir, 'gmx_full_nvt.mdp')
        gro_path = opj(self.data_dir, 'mdrun512_min_gold.gro')
        top_path = opj(self.data_dir, 'genion512_gold.top')
        output_tpr_path = opj(self.results, 'grompp512_nvt.tpr')
        gold_tpr_path = opj(self.data_dir, 'grompp512_nvt_gold.tpr')

        gpp = Grompp512(mdp_path, gro_path, top_path, output_tpr_path)
        gpp.launch()

        self.assertTrue(filecmp.cmp(output_tpr_path, gold_tpr_path))

if __name__ == '__main__':
    unittest.main()
