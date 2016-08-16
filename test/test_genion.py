"""Unittests for gromacs_wrapper.genion module
"""
import unittest
from pymdsetup.gromacs_wrapper.genion import Genion512
import os
from os.path import join as opj


class TestGenion512(unittest.TestCase):

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

    @unittest.skip
    def test_launch(self):
        tpr_path = opj(self.data_dir, 'grompp512_ions_gold.tpr')
        input_top = opj(self.data_dir, 'solvate512_gold.top')
        output_top = opj(self.results, 'genion512.top')
        gold_top_path = opj(self.data_dir, 'genion512_gold.top')
        output_gro_path = opj(self.results, 'genion512.gro')
        gold_gro_path = opj(self.data_dir, 'genion512_gold.gro')

        gio = Genion512(tpr_path, output_gro_path, input_top,
                        output_top, seed=1)
        gio.launch()
        with open(output_gro_path, 'r') as out_file, open(gold_gro_path,
                                                          'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())

        with open(output_top, 'r') as out_top, open(gold_top_path,
                                                    'r') as gold_top:
            out_top_list = " ".join([line if not line.startswith(';')
                                    else '' for line in out_top])
            out_top_gold_list = " ".join([line if not line.startswith(';')
                                         else '' for line in gold_top])
            self.assertItemsEqual(out_top_list, out_top_gold_list)

    @unittest.skipUnless(os.environ.get('PYCOMPSS') is not None,
                         "Skip PyCOMPSs test")
    def test_launchPycompss(self):
        tpr_path = opj(self.data_dir, 'grompp512_ions_gold.tpr')
        input_top = opj(self.data_dir, 'solvate512_gold.top')
        output_top = opj(self.results, 'genion512.top')
        gold_top_path = opj(self.data_dir, 'genion512_gold.top')
        output_gro_path = opj(self.results, 'genion512.gro')
        gold_gro_path = opj(self.data_dir, 'genion512_gold.gro')

        gio = Genion512(tpr_path, output_gro_path, input_top,
                        output_top, seed=1)
        gio.launchPyCOMPSs()
        with open(output_gro_path, 'r') as out_file, open(gold_gro_path,
                                                          'r') as gold_file:
            self.assertMultiLineEqual(out_file.read(), gold_file.read())

        with open(output_top, 'r') as out_top, open(gold_top_path,
                                                    'r') as gold_top:
            out_top_list = " ".join([line if not line.startswith(';')
                                    else '' for line in out_top])
            out_top_gold_list = " ".join([line if not line.startswith(';')
                                         else '' for line in gold_top])
            self.assertItemsEqual(out_top_list, out_top_gold_list)

if __name__ == '__main__':
    unittest.main()
