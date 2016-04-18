"""Unittests for gromacs_wrapper.rms module

@author: pau
"""
import unittest
from pymdsetup.gromacs_wrapper.rms import Rms512
import os
from os.path import join as opj


class TestRms512(unittest.TestCase):

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

    def test_launch(self):
        input_struct = opj(self.data_dir, 'rms_gold.pdb')
        input_traj = opj(self.data_dir, 'rms_gold.xtc')
        output_path = opj(self.results, 'rms.xvg')
        gold_path = opj(self.data_dir, 'rms_gold.xvg')
        rms = Rms512(input_struct, input_traj, output_path)
        rms.launch()
        with open(output_path, 'r') as out_top, open(gold_path,
                                                     'r') as gold_top:
            out_list = " ".join([line if not line.startswith('#') and
                                 not line.startswith('@')
                                else '' for line in out_top])
            out_gold_list = " ".join([line if not line.startswith('#') and
                                      not line.startswith('@')
                                     else '' for line in gold_top])
            self.assertItemsEqual(out_list, out_gold_list)

        self.assertEqual(rms.rmsd, 0.1557643)

    def test_launchPycompss(self):
        input_struct = opj(self.data_dir, 'rms_gold.pdb')
        input_traj = opj(self.data_dir, 'rms_gold.xtc')
        output_path = opj(self.results, 'rms.xvg')
        gold_path = opj(self.data_dir, 'rms_gold.xvg')
        rms = Rms512(input_struct, input_traj, output_path)
        rms.launchPyCOMPSs()
        with open(output_path, 'r') as out_top, open(gold_path,
                                                     'r') as gold_top:
            out_list = " ".join([line if not line.startswith('#') and
                                 not line.startswith('@')
                                else '' for line in out_top])
            out_gold_list = " ".join([line if not line.startswith('#') and
                                      not line.startswith('@')
                                     else '' for line in gold_top])
            self.assertItemsEqual(out_list, out_gold_list)
        self.assertEqual(rms.rmsd, 0.1557643)

if __name__ == '__main__':
    unittest.main()
