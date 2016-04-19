# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb

@author: pau
"""
import os
from os.path import join as opj
from pymdsetup.configuration import settings
from pymdsetup.gromacs_wrapper import pdb2gmx
from pymdsetup.gromacs_wrapper import editconf
from pymdsetup.gromacs_wrapper import solvate
from pymdsetup.gromacs_wrapper import grompp
from pymdsetup.gromacs_wrapper import genion
from pymdsetup.gromacs_wrapper import mdrun
from pymdsetup.gromacs_wrapper import rms
from pymdsetup.mmb_api import pdb
from pymdsetup.mmb_api import uniprot
from pymdsetup.scwrl_wrapper import scwrl
import shutil
import glob


def cdir(wd, name):
    path_sp = opj(wd, name)
    if not os.path.exists(path_sp):
        os.makedirs(path_sp)
    return path_sp


def cext(source_dir, dest_dir, ext):
    files = glob.iglob(os.path.join(source_dir, "*."+ext))
    for file in files:
        if os.path.isfile(file):
            shutil.copy2(file, dest_dir)


def rmtemp():
    # Remove all files in the temp_results directory
    for f in os.listdir('.'):
        try:
            # Not removing directories
            if os.path.isfile(f) and (f.startswith('#') or
               f.startswith('temp') or f.startswith('None') or
               f.startswith('step')):
                os.unlink(f)
        except Exception, e:
            print e


def main():
    #MACOS
    #prop = settings.YamlReader(yaml_path=('/Users/pau/projects/pymdsetup'
    #                                      '/workflows/conf.yaml')).properties
    #Ubunutu
    prop = settings.YamlReader(yaml_path=('/home/pau/projects/pymdsetup'
                                          '/workflows/conf.yaml')).properties
    mdp_dir = os.path.join(os.path.dirname(__file__), 'mdp')
    gmx_path = prop['gmx_path']
    scwrl_path = prop['scwrl4_path']

    wd = os.path.abspath(prop['workflow_path'])
    if not os.path.exists(wd):
        os.makedirs(wd)

    print 'step1: mmbpdb -- Get PDB'
    mmbpdb_path = cdir(wd, 'step1_mmbpdb')
    mmbpdb_pdb = opj(mmbpdb_path, prop['pdb'])
    mmbpdb = pdb.MmbPdb(prop['pdb_code'], mmbpdb_pdb)
    mmbpdb.get_pdb()

    print 'step2: mmbuniprot -- Get mutations'
    mmbuniprot = uniprot.MmbVariants(prop['pdb_code'])
    mutations = mmbuniprot.fetch_variants()

#Demo purposes
########################################################################
    if mmbuniprot.get_uniprot() == 'P00698':
        mutations = ['p.VAL2GLY', 'p.GLY4VAL', 'p.CYS6VAL']
########################################################################

    if mutations is None:
        print (prop['pdb_code'] +
               " " + mmbuniprot.get_uniprot() + ": No variants")
        return


    rmsd_sum = 0
    for mut in mutations:
        mut_path = cdir(wd, mut)

        print 'step3: scw -- Model mutation'
        scw_path = cdir(mut_path, 'step3_scw')
        scw_pdb = opj(scw_path, prop['mutated_pdb'])
        scwrl.Scwrl4(mmbpdb_pdb, scw_pdb, mut, scwrl_path=scwrl_path).launch()

        print 'step4: p2g -- Create gromacs topology'
        p2g_path = cdir(mut_path, 'step4_p2g')
        p2g_gro = opj(p2g_path, prop['p2g_gro'])
        p2g_top = opj(p2g_path, prop['p2g_top'])
        pdb2gmx.Pdb2gmx512(scw_pdb, p2g_gro, p2g_top, gmx_path=gmx_path,
                           ignh=True).launch()

        print 'step5: ec -- Define box dimensions'
        ec_path = cdir(mut_path, 'step5_ec')
        ec_gro = opj(ec_path, prop['ec_gro'])
        editconf.Editconf512(p2g_gro, ec_gro).launch()

        print 'step6: sol -- Fill the box with water molecules'
        sol_path = cdir(mut_path, 'step6_sol')
        cext(p2g_path, sol_path, 'itp')
        sol_gro = opj(sol_path, prop['sol_gro'])
        sol_top = opj(sol_path, prop['sol_top'])
        solvate.Solvate512(ec_gro, sol_gro, p2g_top, sol_top).launch()

        print ('step7: gppions -- Preprocessing:'
               'Add ions to neutralice the charge')
        gppions_path = cdir(mut_path, 'step7_gppions')
        cext(sol_path, gppions_path, 'itp')
        gppions_mdp = opj(gppions_path, prop['gppions_mdp'])
        shutil.copy(opj(mdp_dir, prop['gppions_mdp']), gppions_mdp)
        gppions_tpr = opj(gppions_path, prop['gppions_tpr'])
        grompp.Grompp512(gppions_mdp, sol_gro, sol_top, gppions_tpr).launch()

        print 'step8: gio -- Running: Add ions to neutralice the charge'
        gio_path = cdir(mut_path, 'step8_gio')
        cext(gppions_path, gio_path, 'itp')
        gio_gro = opj(gio_path, prop['gio_gro'])
        gio_top = opj(gio_path, prop['gio_top'])
        genion.Genion512(gppions_tpr, gio_gro, sol_top, gio_top).launch()

        print 'step9: gppmin -- Preprocessing: Energy minimization'
        gppmin_path = cdir(mut_path, 'step9_gppmin')
        cext(gio_path, gppmin_path, 'itp')
        gppmin_mdp = opj(gppmin_path, prop['gppmin_mdp'])
        shutil.copy(opj(mdp_dir, prop['gppmin_mdp']), gppmin_mdp)
        gppmin_tpr = opj(gppmin_path, prop['gppmin_tpr'])
        grompp.Grompp512(gppmin_mdp, gio_gro, gio_top, gppmin_tpr).launch()

        print 'step10: mdmin -- Running: Energy minimization'
        mdmin_path = cdir(mut_path, 'step10_mdmin')
        mdmin_gro = opj(mdmin_path, prop['mdmin_gro'])
        mdmin_trr = opj(mdmin_path, prop['mdmin_trr'])
        mdmin_edr = opj(mdmin_path, prop['mdmin_edr'])
        mdrun.Mdrun512(gppmin_tpr, mdmin_trr, mdmin_gro, mdmin_edr).launch()

        print ('step11: gppnvt -- Preprocessing: nvt'
               'constant number of molecules, volume and temp')
        gppnvt_path = cdir(mut_path, 'step11_gppnvt')
        cext(gio_path, gppnvt_path, 'itp')
        gppnvt_mdp = opj(gppnvt_path, prop['gppnvt_mdp'])
        shutil.copy(opj(mdp_dir, prop['gppnvt_mdp']), gppnvt_mdp)
        gppnvt_tpr = opj(gppnvt_path, prop['gppnvt_tpr'])
        grompp.Grompp512(gppnvt_mdp, mdmin_gro, gio_top, gppnvt_tpr).launch()

        print ('step12: mdnvt -- Running: nvt'
               'constant number of molecules, volume and temp')
        mdnvt_path = cdir(mut_path, 'step12_mdnvt')
        mdnvt_gro = opj(mdnvt_path, prop['mdnvt_gro'])
        mdnvt_trr = opj(mdnvt_path, prop['mdnvt_trr'])
        mdnvt_edr = opj(mdnvt_path, prop['mdnvt_edr'])
        mdnvt_cpt = opj(mdnvt_path, prop['mdnvt_cpt'])
        mdrun.Mdrun512(gppnvt_tpr, mdnvt_trr, mdnvt_gro,
                       mdnvt_edr, output_cpt_path=mdnvt_cpt).launch()

        print ('step13: gppnpt -- Preprocessing: npt'
               'constant number of molecules, pressure and temp')
        gppnpt_path = cdir(mut_path, 'step13_gppnpt')
        cext(gio_path, gppnpt_path, 'itp')
        gppnpt_mdp = opj(gppnpt_path, prop['gppnpt_mdp'])
        shutil.copy(opj(mdp_dir, prop['gppnpt_mdp']), gppnpt_mdp)
        gppnpt_tpr = opj(gppnpt_path, prop['gppnpt_tpr'])
        grompp.Grompp512(gppnpt_mdp, mdnvt_gro, gio_top,
                         gppnpt_tpr, cpt_path=mdnvt_cpt).launch()

        print ('step14: mdnpt -- Running: npt'
               'constant number of molecules, pressure and temp')
        mdnpt_path = cdir(mut_path, 'step14_mdnpt')
        mdnpt_gro = opj(mdnpt_path, prop['mdnpt_gro'])
        mdnpt_trr = opj(mdnpt_path, prop['mdnpt_trr'])
        mdnpt_edr = opj(mdnpt_path, prop['mdnpt_edr'])
        mdnpt_cpt = opj(mdnpt_path, prop['mdnpt_cpt'])
        mdrun.Mdrun512(gppnpt_tpr, mdnpt_trr, mdnpt_gro,
                       mdnpt_edr, output_cpt_path=mdnpt_cpt).launch()

        print ('step15: gppeq -- '
               'Preprocessing: 1ns Molecular dynamics Equilibration')
        gppeq_path = cdir(mut_path, 'step15_gppeq')
        cext(gio_path, gppeq_path, 'itp')
        gppeq_mdp = opj(gppeq_path, prop['gppeq_mdp'])
        shutil.copy(opj(mdp_dir, prop['gppeq_mdp']), gppeq_mdp)
        gppeq_tpr = opj(gppeq_path, prop['gppeq_tpr'])
        grompp.Grompp512(gppeq_mdp, mdnpt_gro, gio_top,
                         gppeq_tpr, cpt_path=mdnpt_cpt).launch()

        print ('step16: mdeq -- '
               'Running: 1ns Molecular dynamics Equilibration')
        mdeq_path = cdir(mut_path, 'step16_mdeq')
        mdeq_gro = opj(mdeq_path, prop['mdeq_gro'])
        mdeq_trr = opj(mdeq_path, prop['mdeq_trr'])
        mdeq_edr = opj(mdeq_path, prop['mdeq_edr'])
        mdeq_cpt = opj(mdeq_path, prop['mdeq_cpt'])
        mdrun.Mdrun512(gppeq_tpr, mdeq_trr, mdeq_gro,
                       mdeq_edr, output_cpt_path=mdeq_cpt).launch()

        print ('step17: rms -- Computing RMSD')
        rms_path = cdir(mut_path, 'step17_rms')
        rms_xvg = opj(rms_path, prop['rms_xvg'])
        rms.Rms512(gio_gro, mdeq_trr, rms_xvg).launch()
        rmsd_sum += rms.rmsd
        rmtemp()

    print "Final RMSD:" + str(rmsd_sum/len(mutations))

if __name__ == '__main__':
    main()
