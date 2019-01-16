#!/usr/bin/env python

"""Python wrapper module for SCWRL
"""
import os
import sys
import json
import numpy as np
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Gnuplot(object):
    """Wrapper class for the 4.6 version of GNUPLOT.
    Args:
        input_xvg_path_dict (dict): Dict where keys are mutations (str) and
                                    values are paths (str) to xvg rmsd files.
        output_png_path (srt): Path to the output png chart file.
        properties (dic):
            output_plotscript_path (str): Path to the output GNUPLOT script file.
            gnuplot_path (str): Path to the GNUPLOT executable binary.
    """
    def __init__(self, input_xvg_path_dict, output_png_path,
                 properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_xvg_path_dict = input_xvg_path_dict
        self.output_png_path = output_png_path
        self.output_plotscript_path = properties.get('output_plotscript_path','gplot.plotscript')
        self.gnuplot_path = properties.get('gnuplot_path',None)
        self.path = properties.get('path','')
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.term = properties.get('term', 'png')

    def launch(self):
        """Launches the execution of the GNUPLOT binary.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        self.output_plotscript_path = fu.add_step_mutation_path_to_name(self.output_plotscript_path, self.step, self.mutation)
        # Create the input script for gnuplot
        xvg_file_list = []
        with open(self.output_plotscript_path, 'w') as ps:
            ps.write('set term '+self.term+'\n')
            ps.write('set output "' + self.output_png_path + '"'+'\n')
            ps.write('plot')
            for k, v in self.input_xvg_path_dict.iteritems():
                if isinstance(v, basestring) and os.path.isfile(v):
                    ps.write(' "' + v + '" u 1:3 w lp t "' + k + '",')
                else:
                    xvg_file = fu.add_step_mutation_path_to_name(k + '.xvg', self.step, self.mutation)
                    np.savetxt(xvg_file, v, fmt='%4.7f')
                    out_log.info('Creating file: '+os.path.abspath(xvg_file))
                    xvg_file_list.append(os.path.abspath(xvg_file))
                    ps.write(' "' + xvg_file + '" u 0:2 w lp t "' + k + '", ')


        gplot = 'gnuplot' if self.gnuplot_path is None else self.gnuplot_path
        cmd = [gplot, self.output_plotscript_path]

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        returncode = command.launch()
        return returncode

#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Gnuplot(input_xvg_path_dict={'mutation':sys.argv[4]},
            output_png_path=sys.argv[5],
            properties=prop).launch()

if __name__ == '__main__':
    main()
