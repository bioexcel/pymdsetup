# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb


"""
import os
from os.path import join as opj

try:
    import configuration.settings as settings
    import gromacs_wrapper.pdb2gmx as pdb2gmx
    import gromacs_wrapper.grompp as grompp
    import scwrl_wrapper.scwrl as scwrl
    import gromacs_wrapper.solvate as solvate
    import gromacs_wrapper.editconf as editconf
    import gromacs_wrapper.genion as genion
    import gromacs_wrapper.mdrun as mdrun
    import mmb_api.pdb as pdb
    import mmb_api.uniprot as uniprot
    import gromacs_wrapper.rms as rms
except ImportError:
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


def cdir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


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
    # MACOS
    conf = settings.YamlReader(yaml_path=('/Users/pau/projects/pymdsetup'
                                          '/workflows/conf.yaml'))
    # Ubunutu
    # conf = settings.YamlReader(yaml_path=('/home/pau/projects/pymdsetup'
    #                                      '/workflows/conf.yaml'))
    # COMPSS VM
    # conf = settings.YamlReader(yaml_path=('/home/compss/PyCOMPSs/git'
    #                                      '/pymdsetup/workflows/conf.yaml'))
    prop = conf.properties
    mdp_dir = os.path.join(os.path.dirname(__file__), 'mdp')
    gmx_path = prop['gmx_path']
    scwrl_path = prop['scwrl4_path']
    input_pdb_code = prop['pdb_code']
    cdir(os.path.abspath(prop['workflow_path']))
    print ''
    print ''
    print '_______GROMACS FULL WORKFLOW_______'
    print ''
    print ''
    print 'step1: mmbpdb -- Get PDB'
    print '     Selected PDB code: ' + input_pdb_code
    p_mmbpdb = conf.step_prop('step1_mmbpdb')
    cdir(p_mmbpdb.path)
    mmbpdb = pdb.MmbPdb(input_pdb_code, p_mmbpdb.pdb)
    mmbpdb.get_pdb()

    print 'step2: mmbuniprot -- Get mutations'
    mmbuniprot = uniprot.MmbVariants(input_pdb_code)
    mutations = mmbuniprot.fetch_variants()
    print '     Uniprot code: ' + mmbuniprot.get_uniprot()

# Demo purposes
########################################################################
    if mmbuniprot.get_uniprot() == 'P00698':
        # mutations = ['p.VAL2GLY', 'p.GLY4VAL', 'p.CYS6VAL']
        mutations = ['p.VAL2GLY']
########################################################################
    print '     Found ' + str(len(mutations)) + ' variants'
    if mutations is None:
        print (prop['pdb_code'] +
               " " + mmbuniprot.get_uniprot() + ": No variants")
        return

    for mut in mutations:
        print ''
        print '___________'
        print mut
        print '-----------'
        print 'step3: scw -- Model mutation'
        p_scw = conf.step_prop('step3_scw', mut)
        cdir(p_scw.path)
        scw = scwrl.Scwrl4(p_mmbpdb.pdb, p_scw.mut_pdb, mut,
                           scwrl_path=scwrl_path, log_path=p_scw.out,
                           error_path=p_scw.err)
        scw.launch()

        print 'step4: p2g -- Create gromacs topology'
        p_p2g = conf.step_prop('step4_p2g', mut)
        cdir(p_p2g.path)
        p2g = pdb2gmx.Pdb2gmx512(p_scw.mut_pdb, p_p2g.gro, p_p2g.top,
                                 gmx_path=gmx_path, ignh=True,
                                 log_path=p_p2g.out, error_path=p_p2g.err)
        p2g.launch()

        print 'step5: ec  -- Define box dimensions'
        p_ec = conf.step_prop('step5_ec', mut)
        cdir(p_ec.path)
        ec = editconf.Editconf512(p_p2g.gro, p_ec.gro, log_path=p_ec.out,
                                  error_path=p_ec.err)
        ec.launch()

        print 'step6: sol -- Fill the box with water molecules'
        p_sol = conf.step_prop('step6_sol', mut)
        cdir(p_sol.path)
        sol = solvate.Solvate512(p_ec.gro, p_sol.gro, p_p2g.top, p_sol.top,
                                 log_path=p_ec.out, error_path=p_ec.err)
        sol.launch()

        # print ('step7: gppions -- Preprocessing:'
        #        'Add ions to neutralice the charge')
        # gppions_path = cdir(mut_path, 'step7_gppions')
        # cext(sol_path, gppions_path, 'itp')
        # gppions_mdp = opj(gppions_path, prop['gppions_mdp'])
        # shutil.copy(opj(mdp_dir, prop['gppions_mdp']), gppions_mdp)
        # gppions_tpr = opj(gppions_path, prop['gppions_tpr'])
        # grompp.Grompp512(gppions_mdp, sol_gro, sol_top, gppions_tpr).launch()
        #
        # print 'step8: gio -- Running: Add ions to neutralice the charge'
        # gio_path = cdir(mut_path, 'step8_gio')
        # cext(gppions_path, gio_path, 'itp')
        # gio_gro = opj(gio_path, prop['gio_gro'])
        # gio_top = opj(gio_path, prop['gio_top'])
        # genion.Genion512(gppions_tpr, gio_gro, sol_top, gio_top).launch()
        #
        # print 'step9: gppmin -- Preprocessing: Energy minimization'
        # gppmin_path = cdir(mut_path, 'step9_gppmin')
        # cext(gio_path, gppmin_path, 'itp')
        # gppmin_mdp = opj(gppmin_path, prop['gppmin_mdp'])
        # shutil.copy(opj(mdp_dir, prop['gppmin_mdp']), gppmin_mdp)
        # gppmin_tpr = opj(gppmin_path, prop['gppmin_tpr'])
        # grompp.Grompp512(gppmin_mdp, gio_gro, gio_top, gppmin_tpr).launch()
        #
        # print 'step10: mdmin -- Running: Energy minimization'
        # mdmin_path = cdir(mut_path, 'step10_mdmin')
        # mdmin_gro = opj(mdmin_path, prop['mdmin_gro'])
        # mdmin_trr = opj(mdmin_path, prop['mdmin_trr'])
        # mdmin_edr = opj(mdmin_path, prop['mdmin_edr'])
        # mdrun.Mdrun512(gppmin_tpr, mdmin_trr, mdmin_gro, mdmin_edr).launch()
        #
        # print ('step11: gppnvt -- Preprocessing: nvt'
        #        'constant number of molecules, volume and temp')
        # gppnvt_path = cdir(mut_path, 'step11_gppnvt')
        # cext(gio_path, gppnvt_path, 'itp')
        # gppnvt_mdp = opj(gppnvt_path, prop['gppnvt_mdp'])
        # shutil.copy(opj(mdp_dir, prop['gppnvt_mdp']), gppnvt_mdp)
        # gppnvt_tpr = opj(gppnvt_path, prop['gppnvt_tpr'])
        # grompp.Grompp512(gppnvt_mdp, mdmin_gro, gio_top, gppnvt_tpr).launch()
        #
        # print ('step12: mdnvt -- Running: nvt'
        #        'constant number of molecules, volume and temp')
        # mdnvt_path = cdir(mut_path, 'step12_mdnvt')
        # mdnvt_gro = opj(mdnvt_path, prop['mdnvt_gro'])
        # mdnvt_trr = opj(mdnvt_path, prop['mdnvt_trr'])
        # mdnvt_edr = opj(mdnvt_path, prop['mdnvt_edr'])
        # mdnvt_cpt = opj(mdnvt_path, prop['mdnvt_cpt'])
        # mdrun.Mdrun512(gppnvt_tpr, mdnvt_trr, mdnvt_gro,
        #                mdnvt_edr, output_cpt_path=mdnvt_cpt).launch()
        #
        # print ('step13: gppnpt -- Preprocessing: npt'
        #        'constant number of molecules, pressure and temp')
        # gppnpt_path = cdir(mut_path, 'step13_gppnpt')
        # cext(gio_path, gppnpt_path, 'itp')
        # gppnpt_mdp = opj(gppnpt_path, prop['gppnpt_mdp'])
        # shutil.copy(opj(mdp_dir, prop['gppnpt_mdp']), gppnpt_mdp)
        # gppnpt_tpr = opj(gppnpt_path, prop['gppnpt_tpr'])
        # grompp.Grompp512(gppnpt_mdp, mdnvt_gro, gio_top,
        #                  gppnpt_tpr, cpt_path=mdnvt_cpt).launch()
        #
        # print ('step14: mdnpt -- Running: npt'
        #        'constant number of molecules, pressure and temp')
        # mdnpt_path = cdir(mut_path, 'step14_mdnpt')
        # mdnpt_gro = opj(mdnpt_path, prop['mdnpt_gro'])
        # mdnpt_trr = opj(mdnpt_path, prop['mdnpt_trr'])
        # mdnpt_edr = opj(mdnpt_path, prop['mdnpt_edr'])
        # mdnpt_cpt = opj(mdnpt_path, prop['mdnpt_cpt'])
        # mdrun.Mdrun512(gppnpt_tpr, mdnpt_trr, mdnpt_gro,
        #                mdnpt_edr, output_cpt_path=mdnpt_cpt).launch()
        #
        # print ('step15: gppeq -- '
        #        'Preprocessing: 1ns Molecular dynamics Equilibration')
        # gppeq_path = cdir(mut_path, 'step15_gppeq')
        # cext(gio_path, gppeq_path, 'itp')
        # gppeq_mdp = opj(gppeq_path, prop['gppeq_mdp'])
        # shutil.copy(opj(mdp_dir, prop['gppeq_mdp']), gppeq_mdp)
        # gppeq_tpr = opj(gppeq_path, prop['gppeq_tpr'])
        # grompp.Grompp512(gppeq_mdp, mdnpt_gro, gio_top,
        #                  gppeq_tpr, cpt_path=mdnpt_cpt).launch()
        #
        # print ('step16: mdeq -- '
        #        'Running: 1ns Molecular dynamics Equilibration')
        # mdeq_path = cdir(mut_path, 'step16_mdeq')
        # mdeq_gro = opj(mdeq_path, prop['mdeq_gro'])
        # mdeq_trr = opj(mdeq_path, prop['mdeq_trr'])
        # mdeq_edr = opj(mdeq_path, prop['mdeq_edr'])
        # mdeq_cpt = opj(mdeq_path, prop['mdeq_cpt'])
        # mdrun.Mdrun512(gppeq_tpr, mdeq_trr, mdeq_gro,
        #                mdeq_edr, output_cpt_path=mdeq_cpt).launch()
        #
        # print ('step17: rms -- Computing RMSD')
        # rms_path = cdir(mut_path, 'step17_rms')
        # rms_xvg = opj(rms_path, prop['rms_xvg'])
        # rms.Rms512(gio_gro, mdeq_trr, rms_xvg).launch()
        print '***************************************************************'
        print ''

        rmtemp()

if __name__ == '__main__':
    main()
