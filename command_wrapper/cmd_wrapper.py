# -*- coding: utf-8 -*-
"""Python wrapper for command line
"""
import subprocess
import os


class CmdWrapper(object):
    """Command line wrapper using subprocess library
    """

    def __init__(self, cmd, out_log=None, err_log=None):

        self.cmd = cmd
        self.out_log = out_log
        self.err_log = err_log

    def launch(self):
        cmd = " ".join(self.cmd)
        if self.out_log is None:
            print ('')
            print ("cmd_wrapper commnand print: " + cmd)
        new_env = os.environ.copy()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True,
                                   env=new_env)

        out, err = process.communicate()
        if self.out_log is None:
            print ("Exit, code {}".format(process.returncode))
        process.wait()

        # Write output to log
        if self.out_log is not None:
            self.out_log.info(cmd+'\n')
            self.out_log.info("Exit code {}".format(process.returncode)+'\n')
            if out is not None:
                self.out_log.info(out)

        if self.err_log is not None:
            if err is not None:
                self.err_log.info(err)

        return process.returncode
