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
                                 water_type=p_p2g.water_type,
                                 force_field=p_p2g.force_field,
                                 ignh=settings.str2bool(p_p2g.ignh),
                                 gmx_path=gmx_path,
                                 log_path=p_p2g.out, error_path=p_p2g.err)
        p2g_compss = p2g.launchPyCOMPSs(scw_pdb_compss)

        print 'step5:  ec ------- Define box dimensions'
        p_ec = conf.step_prop('step5_ec', mut)
        fu.create_dir(p_ec.path)
        ec = editconf.Editconf512(p_p2g.gro, p_ec.gro,
                                  box_type=p_ec.box_type,
                                  distance_to_molecule=float(p_ec.distance_to_molecule),
                                  center_molecule=settings.str2bool(p_ec.center_molecule),
                                  gmx_path=gmx_path,
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
        #fu.copy_ext(p_p2g.path, p_gio.path, 'itp')
        gio = genion.Genion512(p_gppions.tpr, p_gio.gro, p_sol.top, p_gio.top,
                               gmx_path=gmx_path, log_path=p_gio.out,
                               error_path=p_gio.err)
        gio_compss = gio.launchPyCOMPSs(sol_compss, gppions_compss, p_sol.top,
                                        p_gio.top, p_p2g.path, p_gio.path)

        print 'step9:  gppmin --- Preprocessing: Energy minimization'
        p_gppmin = conf.step_prop('step9_gppmin', mut)
        fu.create_dir(p_gppmin.path)
        gppmin = grompp.Grompp512(p_gppmin.mdp, p_gio.gro, p_gio.top,
                                  p_gppmin.tpr, gmx_path=gmx_path,
                                  log_path=p_gppmin.out,
                                  error_path=p_gppmin.err)
        gppmin_compss = gppmin.launchPyCOMPSs(gio_compss,
                                              opj(mdp_dir, prop['step9_gppmin']['mdp']))

        print 'step10: mdmin ---- Running: Energy minimization'
        p_mdmin = conf.step_prop('step10_mdmin', mut)
        fu.create_dir(p_mdmin.path)
        mdmin = mdrun.Mdrun512(p_gppmin.tpr, p_mdmin.trr, p_mdmin.gro,
                               p_mdmin.edr, gmx_path=gmx_path,
                               log_path=p_mdmin.out, error_path=p_mdmin.err)
        mdmin_compss = mdmin.launchPyCOMPSs(gppmin_compss)

        print ('step11: gppnvt --- Preprocessing: nvt '
               'constant number of molecules, volume and temp')
        p_gppnvt = conf.step_prop('step11_gppnvt', mut)
        fu.create_dir(p_gppnvt.path)
        gppnvt = grompp.Grompp512(p_gppnvt.mdp, p_mdmin.gro, p_gio.top,
                                  p_gppnvt.tpr, gmx_path=gmx_path,
                                  log_path=p_gppnvt.out,
                                  error_path=p_gppnvt.err)
        gppnvt_compss = gppnvt.launchPyCOMPSs(mdmin_compss,
                                              opj(mdp_dir, prop['step11_gppnvt']['mdp']))

        print ('step12: mdnvt ---- Running: nvt '
               'constant number of molecules, volume and temp')
        p_mdnvt = conf.step_prop('step12_mdnvt', mut)
        fu.create_dir(p_mdnvt.path)
        mdnvt = mdrun.Mdrun512(p_gppnvt.tpr, p_mdnvt.trr, p_mdnvt.gro,
                               p_mdnvt.edr, gmx_path=gmx_path,
                               output_cpt_path=p_mdnvt.cpt,
                               log_path=p_mdnvt.out, error_path=p_mdnvt.err)
        mdnvt_compss = mdnvt.launchPyCOMPSs(gppnvt_compss)

        print ('step13: gppnpt --- Preprocessing: npt '
               'constant number of molecules, pressure and temp')
        p_gppnpt = conf.step_prop('step13_gppnpt', mut)
        fu.create_dir(p_gppnpt.path)
        gppnpt = grompp.Grompp512(p_gppnpt.mdp, p_mdnvt.gro, p_gio.top,
                                  p_gppnpt.tpr, gmx_path=gmx_path,
                                  cpt_path=p_mdnvt.cpt,
                                  log_path=p_gppnpt.out,
                                  error_path=p_gppnpt.err)
        gppnvt_compss = gppnpt.launchPyCOMPSs(mdnvt_compss,
                                              opj(mdp_dir, prop['step13_gppnpt']['mdp']))

        print ('step14: mdnpt ---- Running: npt '
               'constant number of molecules, pressure and temp')
        p_mdnpt = conf.step_prop('step14_mdnpt', mut)
        fu.create_dir(p_mdnpt.path)
        mdnpt = mdrun.Mdrun512(p_gppnpt.tpr, p_mdnpt.trr, p_mdnpt.gro,
                               p_mdnpt.edr, gmx_path=gmx_path,
                               output_cpt_path=p_mdnpt.cpt,
                               log_path=p_mdnpt.out, error_path=p_mdnpt.err)
        mdnpt_compss = mdnpt.launchPyCOMPSs(gppnvt_compss)

        print ('step15: gppeq ---- '
               'Preprocessing: 1ns Molecular dynamics Equilibration')
        p_gppeq = conf.step_prop('step15_gppeq', mut)
        fu.create_dir(p_gppeq.path)
        shutil.copy(opj(mdp_dir, prop['step15_gppeq']['mdp']), p_gppeq.mdp)
        gppeq = grompp.Grompp512(p_gppeq.mdp, p_mdnpt.gro, p_gio.top,
                                 p_gppeq.tpr, cpt_path=p_mdnpt.cpt,
                                 gmx_path=gmx_path,
                                 log_path=p_gppeq.out,
                                 error_path=p_gppeq.err)
        gppeq_compss = gppeq.launchPyCOMPSs(mdnpt_compss,
                                            opj(mdp_dir, prop['step15_gppeq']['mdp']))

        print ('step16: mdeq ----- '
               'Running: 1ns Molecular dynamics Equilibration')
        p_mdeq = conf.step_prop('step16_mdeq', mut)
        fu.create_dir(p_mdeq.path)
        mdeq = mdrun.Mdrun512(p_gppeq.tpr, p_mdeq.trr, p_mdeq.gro,
                              p_mdeq.edr, output_cpt_path=p_mdeq.cpt,
                              gmx_path=gmx_path, log_path=p_mdeq.out,
                              error_path=p_mdeq.err)
        mdeq_compss = mdeq.launchPyCOMPSs(gppeq_compss)

        print ('step17: rmsd ----- Computing RMSD')
        p_rmsd = conf.step_prop('step17_rmsd', mut)
        fu.create_dir(p_rmsd.path)
        rmsd = rms.Rms512(p_gio.gro, p_mdeq.trr, p_rmsd.xvg,
                          log_path=p_rmsd.out, error_path=p_rmsd.err)
        # rmsd_list.append(grorms.launchPyCOMPSs(mdeq_compss))
        print '***************************************************************'
        print ''

        fu.rm_temp()
        break

    #result = mdrun.Mdrun512.mergeResults(rmsd_list)

if __name__ == '__main__':
    main()
