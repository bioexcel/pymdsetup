"""Unittests for structure.db module
"""
import unittest
from pymdsetup.scwrl_wrapper.scwrl import Scwrl4
import os
from os.path import join as opj


class TestScwrl(unittest.TestCase):

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
        mutation = 'A.His11Asp'
        output_path = opj(self.results, 'scwrl4.pdb')
        output_gold_path = opj(self.data_dir, 'scwrl4_gold.pdb')
        output_prepared_path = opj(self.results,
                                   'scwrl4.pdb.scwrl4.prepared.pdb')
        gold_prepared_path = opj(self.data_dir, 'gold.scwrl4.prepared.pdb')
        input_scwrl_path = opj(self.data_dir, 'gold.scwrl4.input.pdb')
        sc = Scwrl4(input_scwrl_path, output_path, mutation)
        sc.launch()
        with open(output_prepared_path,
                  'r') as out_file, open(gold_prepared_path, 'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())
        with open(output_path,
                  'r') as out_file, open(output_gold_path, 'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())

    @unittest.skipUnless(os.environ.get('PYCOMPSS') is not None,
                         "Skip PyCOMPSs test")
    def test_launchPycompss(self):
        mutation = 'A.His11Asp'
        output_path = opj(self.results, 'scwrl4.pdb')
        output_gold_path = opj(self.data_dir, 'scwrl4_gold.pdb')
        output_prepared_path = opj(self.results,
                                   'scwrl4.pdb.scwrl4.prepared.pdb')
        gold_prepared_path = opj(self.data_dir, 'gold.scwrl4.prepared.pdb')
        input_scwrl_path = opj(self.data_dir, 'gold.scwrl4.input.pdb')
        sc = Scwrl4(input_scwrl_path, output_path, mutation)
        sc.launchPyCOMPSs()
        with open(output_prepared_path,
                  'r') as out_file, open(gold_prepared_path, 'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())
        with open(output_path,
                  'r') as out_file, open(output_gold_path, 'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())


if __name__ == '__main__':
    unittest.main()
