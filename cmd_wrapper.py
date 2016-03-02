# -*- coding: utf-8 -*-
"""Python wrapper for subprocess library

@author: pau
"""

import subprocess


class CmdWrapper(object):
    """Wrapper for the 5.1.2 version of the pdb2gmx module
    """

    def __init__(self, cmd, log_path=None, error_path=None):
        self.log_path = log_path
        self.error_path = error_path
        self.cmd = cmd

    def launch(self):

        process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        out, err = process.communicate()

        # Write output to log_file
        if self.log_path is not None:
            with open(self.log_path, 'a') as log_file:
                log_file.writte(out)

        if self.error_path is not None:
            with open(self.error_path, 'a') as error_file:
                error_file.writte(err)
