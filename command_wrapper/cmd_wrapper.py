# -*- coding: utf-8 -*-
"""Python wrapper for command line

@author: pau
"""
import subprocess
import os.path as op
import shutil
import os


class CmdWrapper(object):
    """Command line wrapper using subprocess library
    """

    def __init__(self, cmd, log_path=None, error_path=None):
        self.log_path = log_path
        if self.log_path == 'None':
            self.log_path = None
        self.error_path = error_path
        if self.error_path == 'None':
            self.error_path = None
        self.cmd = cmd

    def launch(self):
        cmd = " ".join(self.cmd)
        if self.log_path is None:
            print ''
            print "cmd_wrapper commnand print: " + cmd
        new_env = os.environ.copy()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True,
                                   env=new_env)

        out, err = process.communicate()
        if self.log_path is None:
            print "Exit, code {}".format(process.returncode)
        process.wait()

        # Write output to log_file
        if self.log_path is not None:
            with open(self.log_path, 'w') as log_file:
                log_file.write(cmd+'\n')
                log_file.write("Exit code {}".format(process.returncode)+'\n')
                if out is not None:
                    log_file.write(out)

        if self.error_path is not None:
            with open(self.error_path, 'w') as error_file:
                if err is not None:
                    error_file.write(err)

    def move_file_output(self, file_name, dest_dir):
        if op.exists(file_name):
                if not op.exists(op.join(dest_dir, file_name)):
                    shutil.move(file_name, dest_dir)
                else:
                    n = 1
                    while op.exists(op.join(dest_dir,
                                            file_name + '.' + str(n))):
                        n += 1
                    shutil.move(file_name, op.join(dest_dir,
                                                   file_name + '.' + str(n)))
