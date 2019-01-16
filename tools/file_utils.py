"""Tools to work with files
"""
import os
import shutil
import glob
import zipfile
import logging
from os.path import join as opj

def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def get_workflow_path(dir_path):
    if not os.path.exists(dir_path):
        return dir_path

    cont = 1
    while os.path.exists(dir_path):
        dir_path = dir_path.rstrip('\\/0123456789_') + '_' + str(cont)
        cont += 1
    return dir_path

def remove_temp_files(endswith_list, source_dir=None):
    removed_list = []
    source_dir = os.getcwd() if source_dir is None else os.path.abspath(source_dir)
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    for f in files:
        if f.endswith(tuple(endswith_list)):
            os.remove(f)
            removed_list.append(f)
    return removed_list

def zip_top(top_file, zip_file, remove_files=False, out_log=None, mutation=None):
    if out_log:
        out_log.info('')
        out_log.info('********************************* zip_top function *********************************')
        out_log.info('')
    top_dir = os.path.abspath(os.path.dirname(top_file))
    if mutation:
        files = [os.path.join(top_dir,fname) for fname in os.listdir(top_dir) if fname.startswith(mutation) and fname.endswith('.itp')]
        if os.path.abspath(os.getcwd()) != top_dir:
            files += [os.path.join(os.getcwd(),fname) for fname in os.listdir(os.getcwd()) if fname.startswith(mutation) and fname.endswith('.itp')]
    else:
        files = [os.path.join(top_dir,fname) for fname in os.listdir(top_dir) if fname.endswith('.itp')]
        if os.path.abspath(os.getcwd()) != top_dir:
            files += [os.path.join(os.getcwd(),fname) for fname in os.listdir(os.getcwd()) if fname.endswith('.itp')]
    if out_log:
        out_log.info('Files to compress:')
        for fname in files:
            out_log.info(fname)
        out_log.info('top_file: '+top_file)

    with zipfile.ZipFile(zip_file, 'w') as zip_open:
        for f in files:
            zip_open.write(f, arcname=os.path.basename(f))
            if remove_files: os.remove(f)
        zip_open.write(top_file, arcname=os.path.basename(top_file))
        if remove_files: os.remove(top_file)

    if out_log:
        out_log.info('')
        out_log.info('********************************* END zip_top function *********************************')
        out_log.info('')

def unzip_top(zip_file, dest_dir=None, top_file=None, out_log=None):
    if out_log:
        out_log.info('')
        out_log.info('********************************* unzip_top function *********************************')
        out_log.info('')
        out_log.info('This is the unzip, zip_file: ')
        out_log.info(zip_file)
    if not dest_dir:
        dest_dir=os.getcwd()
    if out_log:
        out_log.info('dest_dir: '+dest_dir)
    if not os.path.exists(dest_dir):
        if out_log:
            out_log.info(dest_dir+' does not exists creating it')
        os.mkdir(dest_dir)
        if out_log:
            out_log.info(dest_dir+' succesfully created')
    if out_log:
        out_log.info('zipfile: ')
        out_log.info(zip_file)
    with zipfile.ZipFile(zip_file) as zip_open:
        if out_log:
            out_log.info('Decompressing file list:')
        for fname in zip_open.namelist():
            if out_log:
                out_log.info(fname)
            if fname.endswith(".top"):
                zip_name = fname
                if out_log:
                    out_log.info('zip_name found: '+zip_name)

        zip_open.extractall(path=dest_dir)

    if top_file:
        top_file=os.path.join(dest_dir, os.path.basename(top_file))
        out_log.info('copy: '+os.path.join(dest_dir, zip_name)+'to: '+top_file)
        shutil.copyfile(os.path.join(dest_dir, zip_name), top_file)
    else:
        top_file = os.path.join(dest_dir,zip_name)
    if out_log:
        out_log.info('files in '+dest_dir+':')
        for fname in os.listdir(dest_dir):
            out_log.info(fname)
        out_log.info('')
        out_log.info('returned top_file: '+top_file)
        out_log.info('')
        out_log.info('********************************* END unzip_top function *********************************')
        out_log.info('')
    return top_file


def get_logs(path, mutation=None, step=None, console=False, level='INFO'):
    out_log_path = add_step_mutation_path_to_name('out.log', step, mutation, path)
    err_log_path = add_step_mutation_path_to_name('err.log', step, mutation, path)
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    out_Logger = logging.getLogger(out_log_path)
    out_Logger.setLevel(level)
    err_Logger = logging.getLogger(err_log_path)
    err_Logger.setLevel(level)

    #Creating and formating FileHandler
    out_fileHandler = logging.FileHandler(out_log_path, mode='a', encoding=None, delay=False)
    err_fileHandler = logging.FileHandler(err_log_path, mode='a', encoding=None, delay=False)
    out_fileHandler.setFormatter(logFormatter)
    err_fileHandler.setFormatter(logFormatter)

    #Asign FileHandler
    out_Logger.addHandler(out_fileHandler)
    err_Logger.addHandler(err_fileHandler)

    #Creating and formating consoleHandler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)

    # Adding console aditional output
    if console:
        out_Logger.addHandler(consoleHandler)
        err_Logger.addHandler(consoleHandler)

    out_Logger.setLevel(10)
    err_Logger.setLevel(10)
    return out_Logger, err_Logger

def human_readable_time(time_ps):
    time_units = ['femto seconds','pico seconds','nano seconds','micro seconds','mili seconds']
    time = time_ps * 1000
    for tu in time_units:
        if time < 1000:
            return str(time)+' '+tu
        else:
            time = time/1000
    return str(time_ps)

def add_step_mutation_path_to_name(name, step=None, mutation=None, path=None):
    if step:
        name = step+'_'+name
    if mutation:
        name = mutation+'_'+name
    if path:
        name = opj(path, name)
    return name
