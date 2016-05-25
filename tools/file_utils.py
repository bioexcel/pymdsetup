# -*- coding: utf-8 -*-
"""Tools to work with files

"""
import os
import shutil
import glob


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def copy_ext(source_dir, dest_dir, ext):
    files = glob.iglob(os.path.join(source_dir, "*."+ext))
    for file in files:
        if os.path.isfile(file):
            shutil.copy2(file, dest_dir)


def rm_temp():
    # Remove all files in the temp_results directory
    for f in os.listdir('.'):
        try:
            # Not removing directories
            if os.path.isfile(f) and (f.startswith('#') or
               f.startswith('temp') or f.startswith('None') or
               f.startswith('step')):
                os.unlink(f)
            # elif os.path.isdir(f) and (f.startswith('pycompss')):
            #     shutil.rmtree(f)
        except Exception, e:
            print e
