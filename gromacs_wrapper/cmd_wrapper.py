# -*- coding: utf-8 -*-
"""Python wrapper for command line

@author: pau
"""
import subprocess


class CmdWrapper(object):
    """Command line wrapper using subprocess library
    """

    def __init__(self, cmd, log_path=None, error_path=None):
        self.log_path = log_path
        self.error_path = error_path
        self.cmd = cmd

    def launch(self):

        n_commands = 0
        commands = [[]]
        for argument in self.cmd:
            if argument == "|":
                n_commands += 1
                commands.append([])
            else:
                commands[n_commands].append(argument)
        if n_commands > 0:
            process_list = []
            for i in range(len(commands)):
                if i == 0:
                    process_list.append(subprocess.Popen(commands[i],
                                        stdout=subprocess.PIPE))
                else:
                    process_list.append(subprocess.Popen(commands[i],
                                        stdin=process_list[i-1],
                                        stdout=subprocess.PIPE))
                    process_list[i-1].stdout.close()

            out, err = process_list[-1].communicate()
        else:
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
