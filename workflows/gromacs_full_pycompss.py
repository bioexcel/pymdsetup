# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb


"""
import os
import shutil
from os.path import join as opj

try:
    import tools.file_utils as fu
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
    from pymdsetup.tools import file_utils as fu
    from pymdsetup.configuration import settings
    from pymdsetup.gromacs_wrapper import pdb2gmx
    from pymdsetup.gromacs_wrapper import grompp
    from pymdsetup.scwrl_wrapper import scwrl
    from pymdsetup.gromacs_wrapper import solvate
    from pymdsetup.gromacs_wrapper import editconf
    from pymdsetup.gromacs_wrapper import genion
    from pymdsetup.gromacs_wrapper import mdrun
    from pymdsetup.mmb_api import pdb
    from pymdsetup.mmb_api import uniprot
    from pymdsetup.gromacs_wrapper import rms


def main():
    # COMPSS VM
    conf = settings.YamlReader(yaml_path=('/home/compss'
                                          '/pymdsetup/workflows/conf.yaml'))

    prop = conf.properties
    mdp_dir = prop['mdp_path']
    gmx_path = prop['gmx_path']
    scwrl_path = prop['scwrl4_path']
    input_pdb_code = prop['pdb_code']
    fu.create_dir(os.path.abspath(prop['workflow_path']))

    # Testing purposes: Remove last Test
    shutil.rmtree(prop['workflow_path'])

    print ''
    print ''
    print '_______GROMACS FULL WORKFLOW_______'
    print ''
    print ''
    print 'step1:  mmbpdb -- Get PDB'
    print '     Selected PDB code: ' + input_pdb_code
    p_mmbpdb = conf.step_prop('step1_mmbpdb')
    fu.create_dir(p_mmbpdb.path)
    mmbpdb = pdb.MmbPdb(input_pdb_code, p_mmbpdb.pdb)
    mmbpdb.get_pdb()

    print 'step2:  mmbuniprot -- Get mutations'
    mmbuniprot = uniprot.MmbVariants(input_pdb_code)
    mutations = mmbuniprot.get_pdb_variants()
    print '     Uniprot code: ' + mmbuniprot.get_uniprot()

# Demo purposes
########################################################################
    if mmbuniprot.get_uniprot() == 'P00698':
        # mutations = ['A.VAL2GLY', 'A.GLY4VAL', 'A.CYS6VAL']
        mutations = ['A.VAL2GLY']
########################################################################

    # if mutations is None or len(mutations) == 0:
    #     print (prop['pdb_code'] +
    #            " " + mmbuniprot.get_uniprot() + ": No variants")
    #     return
    # else:
    #     print ('     Found ' + str(len(mmbuniprot.get_variants())) +
    #            ' uniprot variants')
    #     print ('     Mapped to ' + str(len(mutations)) + ' ' + input_pdb_code +
    #            ' PDB variants')

    for mut in mutations:
        print ''
        print '___________'
        print mut
        print '-----------'
        print 'step3:  scw ------ Model mutation'
        p_scw = conf.step_prop('step3_scw', mut)
        fu.create_dir(p_scw.path)
        scw = scwrl.Scwrl4(p_mmbpdb.pdb, p_scw.mut_pdb, mut,
                           scwrl_path=scwrl_path, log_path=p_scw.out,
                           error_path=p_scw.err)
        scw_pdb_compss = scw.launchPyCOMPSs()

        print 'step4:  p2g ------ Create gromacs topology'
        p_p2g = conf.step_prop('step4_p2g', mut)
        fu.create_dir(p_p2g.path)
        p2g = pdb2gmx.Pdb2gmx512(p_scw.mut_pdb, p_p2g.gro, p_p2g.top,
                                 gmx_path=gmx_path, ignh=True,
                                 log_path=p_p2g.out, error_path=p_p2g.err)
        p2g_compss = p2g.launchPyCOMPSs(scw_pdb_compss)

        print 'step5:  ec ------- Define box dimensions'
        p_ec = conf.step_prop('step5_ec', mut)
        fu.create_dir(p_ec.path)
        ec = editconf.Editconf512(p_p2g.gro, p_ec.gro, gmx_path=gmx_path,
                                  log_path=p_ec.out, error_path=p_ec.err)
        ec_compss = ec.launchPyCOMPSs(p2g_compss)

        print 'step6:  sol ------ Fill the box with water molecules'
        p_sol = conf.step_prop('step6_sol', mut)
        fu.create_dir(p_sol.path)
        sol = solvate.Solvate512(p_ec.gro, p_sol.gro, p_p2g.top, p_sol.top,
                                 gmx_path=gmx_path, log_path=p_sol.out,
                                 error_path=p_sol.err)
        # sol_ IN = p_p2g.top, OUT=p_sol.top
        sol_compss = sol.launchPyCOMPSs(p2g_compss, ec_compss, p_p2g.top,
                                        p_sol.top)

        print ('step7:  gppions -- Preprocessing: '
               'Add ions to neutralice the charge')
        p_gppions = conf.step_prop('step7_gppions', mut)
        fu.create_dir(p_gppions.path)
        gppions = grompp.Grompp512(p_gppions.mdp, p_sol.gro, p_sol.top,
                                   p_gppions.tpr, gmx_path=gmx_path,
                                   log_path=p_gppions.out,
                                   error_path=p_gppions.err)
        gppions_compss = gppions.launchPyCOMPSs(sol_compss,
                                                opj(mdp_dir, prop['step7_gppions']['mdp']))

        print 'step8:  gio -- Running: Add ions to neutralice the charge'
        p_gio = conf.step_prop('step8_gio', mut)
        fu.create_dir(p_gio.path)
        fu.copy_ext(p_p2g.path, p_gio.path, 'itp')
        gio = genion.Genion512(p_gppions.tpr, p_gio.gro, p_sol.top, p_gio.top,
                               gmx_path=gmx_path, log_path=p_gio.out,
                               error_path=p_gio.err)
        gio_compss = gio.launchPyCOMPSs(sol_compss, gppions_compss, p_sol.top,
                                        p_gio.top)

        print 'step9:  gppmin --- Preprocessing: Energy minimization'
        p_gppmin = conf.step_prop('step9_gppmin', mut)
        fu.create_dir(p_gppmin.path)
        gppmin = grompp.Grompp512(p_gppmin.mdp, p_gio.gro, p_gio.top,
                                  p_gppmin.tpr, gmx_path=gmx_path,
                                  log_path=p_gppmin.out,
                                  error_path=p_gppmin.err)
        gppmin_compss = gppmin.launchPyCOMPSs(gio_compss,
                                              opj(mdp_dir, prop['step9_gppmin']['mdp']))
        # print 'step10: mdmin -- Running: Energy minimization'
        # mdmin_path = cdir(mut_path, 'step10_mdmin')
        # mdmin_gro = opj(mdmin_path, prop['mdmin_gro'])
        # mdmin_trr = opj(mdmin_path, prop['mdmin_trr'])
        # mdmin_edr = opj(mdmin_path, prop['mdmin_edr'])
        # mdmin = mdrun.Mdrun512(gppmin_tpr, mdmin_trr, mdmin_gro, mdmin_edr,
        #                        gmx_path=gmx_path)
        # md1 = mdmin.launchPyCOMPSs(gro3)
        #
        # print ('step11: gppnvt -- Preprocessing: nvt'
        #        'constant number of molecules, volume and temp')
        # gppnvt_path = cdir(mut_path, 'step11_gppnvt')
        # cext(gio_path, gppnvt_path, 'itp')
        # gppnvt_mdp = opj(gppnvt_path, prop['gppnvt_mdp'])
        # shutil.copy(opj(mdp_dir, prop['gppnvt_mdp']), gppnvt_mdp)
        # gppnvt_tpr = opj(gppnvt_path, prop['gppnvt_tpr'])
        # gppnvt = grompp.Grompp512(gppnvt_mdp, mdmin_gro, gio_top, gppnvt_tpr,
        #                           gmx_path=gmx_path)
        # gppnvt1 = gppnvt.launchPyCOMPSs(gen2, md1)
        #
        # print ('step12: mdnvt -- Running: nvt'
        #        'constant number of molecules, volume and temp')
        # mdnvt_path = cdir(mut_path, 'step12_mdnvt')
        # mdnvt_gro = opj(mdnvt_path, prop['mdnvt_gro'])
        # mdnvt_trr = opj(mdnvt_path, prop['mdnvt_trr'])
        # mdnvt_edr = opj(mdnvt_path, prop['mdnvt_edr'])
        # mdnvt_cpt = opj(mdnvt_path, prop['mdnvt_cpt'])
        # mdnvt = mdrun.Mdrun512(gppnvt_tpr, mdnvt_trr, mdnvt_gro, mdnvt_edr,
        #                        output_cpt_path=mdnvt_cpt, gmx_path=gmx_path)
        # mdnvt1 = mdnvt.launchPyCOMPSs(gppnvt1)
        #
        # print ('step13: gppnpt -- Preprocessing: npt'
        #        'constant number of molecules, pressure and temp')
        # gppnpt_path = cdir(mut_path, 'step13_gppnpt')
        # cext(gio_path, gppnpt_path, 'itp')
        # gppnpt_mdp = opj(gppnpt_path, prop['gppnpt_mdp'])
        # shutil.copy(opj(mdp_dir, prop['gppnpt_mdp']), gppnpt_mdp)
        # gppnpt_tpr = opj(gppnpt_path, prop['gppnpt_tpr'])
        # gppnpt = grompp.Grompp512(gppnpt_mdp, mdnvt_gro, gio_top, gppnpt_tpr,
        #                           cpt_path=mdnvt_cpt, gmx_path=gmx_path)
        # gppnvt2 = gppnpt.launchPyCOMPSs(gen2, mdnvt1)
        #
        # print ('step14: mdnpt -- Running: npt'
        #        'constant number of molecules, pressure and temp')
        # mdnpt_path = cdir(mut_path, 'step14_mdnpt')
        # mdnpt_gro = opj(mdnpt_path, prop['mdnpt_gro'])
        # mdnpt_trr = opj(mdnpt_path, prop['mdnpt_trr'])
        # mdnpt_edr = opj(mdnpt_path, prop['mdnpt_edr'])
        # mdnpt_cpt = opj(mdnpt_path, prop['mdnpt_cpt'])
        # mdnpt = mdrun.Mdrun512(gppnpt_tpr, mdnpt_trr, mdnpt_gro, mdnpt_edr,
        #                        output_cpt_path=mdnpt_cpt, gmx_path=gmx_path)
        # mdnpt1 = mdnpt.launchPyCOMPSs(gppnvt2)
        #
        # print ('step15: gppeq -- '
        #        'Preprocessing: 1ns Molecular dynamics Equilibration')
        # gppeq_path = cdir(mut_path, 'step15_gppeq')
        # cext(gio_path, gppeq_path, 'itp')
        # gppeq_mdp = opj(gppeq_path, prop['gppeq_mdp'])
        # shutil.copy(opj(mdp_dir, prop['gppeq_mdp']), gppeq_mdp)
        # gppeq_tpr = opj(gppeq_path, prop['gppeq_tpr'])
        # gppeq = grompp.Grompp512(gppeq_mdp, mdnpt_gro, gio_top, gppeq_tpr,
        #                          cpt_path=mdnpt_cpt, gmx_path=gmx_path)
        # gppeq1 = gppeq.launchPyCOMPSs(gen2, mdnpt1)
        #
        # print ('step16: mdeq -- '
        #        'Running: 1ns Molecular dynamics Equilibration')
        # mdeq_path = cdir(mut_path, 'step16_mdeq')
        # mdeq_gro = opj(mdeq_path, prop['mdeq_gro'])
        # mdeq_trr = opj(mdeq_path, prop['mdeq_trr'])
        # mdeq_edr = opj(mdeq_path, prop['mdeq_edr'])
        # mdeq_cpt = opj(mdeq_path, prop['mdeq_cpt'])
        # mdeq = mdrun.Mdrun512(gppeq_tpr, mdeq_trr, mdeq_gro, mdeq_edr,
        #                       output_cpt_path=mdeq_cpt, gmx_path=gmx_path)
        # mdeq1 = mdeq.launchPyCOMPSs(gppeq1)
        #
        # print ('step17: rms -- Computing RMSD')
        # rms_path = cdir(mut_path, 'step17_rms')
        # rms_xvg = opj(rms_path, prop['rms_xvg'])
        # grorms = rms.Rms512(gio_gro, mdeq_trr, rms_xvg, gmx_path=gmx_path)
        # rmsd_list.append(grorms.launchPyCOMPSs(mdeq1))
        print '***************************************************************'
        print ''

        fu.rm_temp()
        break

    #result = mdrun.Mdrun512.mergeResults(rmsd_list)

if __name__ == '__main__':
    main()
