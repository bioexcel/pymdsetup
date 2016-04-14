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

    def test_launch_minimization(self):
        tpr_path = opj(self.data_dir, 'grompp512_min_gold.tpr')
        trr_path = opj(self.results, 'mdrun512_min.trr')
        gold_trr_path = opj(self.data_dir, 'mdrun512_min_gold.trr')
        gro_path = opj(self.results, 'mdrun512_min.gro')
        gold_gro_path = opj(self.data_dir, 'mdrun512_min_gold.gro')
        edr_path = opj(self.results, 'mdrun512_min.edr')
        gold_edr_path = opj(self.data_dir, 'mdrun512_min_gold.edr')
        mdr = Mdrun512(tpr_path, trr_path, gro_path, edr_path)
        mdr.launch()

        self.assertTrue(filecmp.cmp(trr_path, gold_trr_path))
        self.assertTrue(filecmp.cmp(gro_path, gold_gro_path))
        self.assertTrue(filecmp.cmp(edr_path, gold_edr_path))

    def test_launch_minimizationPycompss(self):
        tpr_path = opj(self.data_dir, 'grompp512_min_gold.tpr')
        trr_path = opj(self.results, 'mdrun512_min.trr')
        gold_trr_path = opj(self.data_dir, 'mdrun512_min_gold.trr')
        gro_path = opj(self.results, 'mdrun512_min.gro')
        gold_gro_path = opj(self.data_dir, 'mdrun512_min_gold.gro')
        edr_path = opj(self.results, 'mdrun512_min.edr')
        gold_edr_path = opj(self.data_dir, 'mdrun512_min_gold.edr')
        mdr = Mdrun512(tpr_path, trr_path, gro_path, edr_path)
        mdr.launchPyCOMPSs()

        self.assertTrue(filecmp.cmp(trr_path, gold_trr_path))
        self.assertTrue(filecmp.cmp(gro_path, gold_gro_path))
        self.assertTrue(filecmp.cmp(edr_path, gold_edr_path))

    # def test_launch_nvt(self):
    #     tpr_path = opj(self.data_dir, 'grompp512_nvt_gold.tpr')
    #     trr_path = opj(self.results, 'mdrun512_nvt.trr')
    #     gold_trr_path = opj(self.data_dir, 'mdrun512_nvt_gold.trr')
    #     gro_path = opj(self.results, 'mdrun512_nvt.gro')
    #     gold_gro_path = opj(self.data_dir, 'mdrun512_nvt_gold.gro')
    #     edr_path = opj(self.results, 'mdrun512_nvt.edr')
    #     gold_edr_path = opj(self.data_dir, 'mdrun512_nvt_gold.edr')
    #     cpt_path = opj(self.results, 'mdrun512_nvt.cpt')
    #     gold_cpt_path = opj(self.data_dir, 'mdrun512_nvt_gold.cpt')
    #     mdr = Mdrun512(tpr_path, trr_path, gro_path, edr_path,
    #                    output_cpt_path=cpt_path)
    #     mdr.launch()

    #     self.assertTrue(filecmp.cmp(trr_path, gold_trr_path))
    #     self.assertTrue(filecmp.cmp(gro_path, gold_gro_path))
    #     self.assertTrue(filecmp.cmp(edr_path, gold_edr_path))
    #     self.assertTrue(filecmp.cmp(cpt_path, gold_cpt_path))

    # def test_launch_npt(self):
    #     tpr_path = opj(self.data_dir, 'grompp512_npt_gold.tpr')
    #     trr_path = opj(self.results, 'mdrun512_npt.trr')
    #     gold_trr_path = opj(self.data_dir, 'mdrun512_npt_gold.trr')
    #     gro_path = opj(self.results, 'mdrun512_npt.gro')
    #     gold_gro_path = opj(self.data_dir, 'mdrun512_npt_gold.gro')
    #     edr_path = opj(self.results, 'mdrun512_npt.edr')
    #     gold_edr_path = opj(self.data_dir, 'mdrun512_npt_gold.edr')
    #     cpt_path = opj(self.results, 'mdrun512_npt.cpt')
    #     gold_cpt_path = opj(self.data_dir, 'mdrun512_npt_gold.cpt')
    #     mdr = Mdrun512(tpr_path, trr_path, gro_path, edr_path,
    #                    output_cpt_path=cpt_path)
    #     mdr.launch()

    #     self.assertTrue(filecmp.cmp(trr_path, gold_trr_path))
    #     self.assertTrue(filecmp.cmp(gro_path, gold_gro_path))
    #     self.assertTrue(filecmp.cmp(edr_path, gold_edr_path))
    #     self.assertTrue(filecmp.cmp(cpt_path, gold_cpt_path))

    # def test_launch_md(self):
    #     tpr_path = opj(self.data_dir, 'grompp512_md_gold.tpr')
    #     trr_path = opj(self.results, 'mdrun512_md.trr')
    #     gold_trr_path = opj(self.data_dir, 'mdrun512_md_gold.trr')
    #     gro_path = opj(self.results, 'mdrun512_md.gro')
    #     gold_gro_path = opj(self.data_dir, 'mdrun512_md_gold.gro')
    #     edr_path = opj(self.results, 'mdrun512_md.edr')
    #     gold_edr_path = opj(self.data_dir, 'mdrun512_md_gold.edr')
    #     cpt_path = opj(self.results, 'mdrun512_md.cpt')
    #     gold_cpt_path = opj(self.data_dir, 'mdrun512_md_gold.cpt')
    #     mdr = Mdrun512(tpr_path, trr_path, gro_path, edr_path,
    #                    output_cpt_path=cpt_path)
    #     mdr.launch()

    #     self.assertTrue(filecmp.cmp(trr_path, gold_trr_path))
    #     self.assertTrue(filecmp.cmp(gro_path, gold_gro_path))
    #     self.assertTrue(filecmp.cmp(edr_path, gold_edr_path))
    #     self.assertTrue(filecmp.cmp(cpt_path, gold_cpt_path))

if __name__ == '__main__':
    unittest.main()
