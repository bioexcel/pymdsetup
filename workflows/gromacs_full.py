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
from pymdsetup.mmb_api import pdb
from pymdsetup.mmb_api import uniprot
from pymdsetup.scwrl_wrapper import scwrl


def cdir(wd, name):
    print wd
    path_sp = opj(wd, name)
    print path_sp
    if not os.path.exists(path_sp):
        os.makedirs(path_sp)
    return path_sp

prop = settings.YamlReader(yaml_path='/home/pau/projects/pymdsetup/workflows/conf.yaml').properties
mdp_dir = os.path.join(os.path.dirname(__file__), 'mdp')
gmx_path = prop['gmx_path']
scwrl_path = prop['scwrl4_path']

wd = os.path.abspath(prop['workflow_path'])
if not os.path.exists(wd):
    os.makedirs(wd)

# Step1: mmbpdb -- Get PDB
mmbpdb_path = cdir(wd, 'step1_mmbpdb')
print mmbpdb_path
mmbpdb_pdb = opj(mmbpdb_path, prop['pdb'])
mmbpdb = pdb.MmbPdb(prop['pdb_code'], mmbpdb_pdb)
mmbpdb.get_pdb()

# Step2: mmbuniprot -- Get mutations
mmbuniprot = uniprot.MmbVariants(prop['pdb_code'])
mutations = mmbuniprot.fetch_variants()

for mut in mutations:
    mut_path = cdir(wd, mut)

    # Step3: scw -- Model mutation
    scw_path = cdir(mut_path, 'step3_scw')
    scw_pdb = opj(scw_path, prop['mutated_pdb'])
    scw = scwrl.Scwrl4(mmbpdb_pdb, scw_pdb, mut,
                       scwrl_path=scwrl_path).launch()

    # Step4: p2g -- Create gromacs topology
    p2g_path = cdir(mut_path, 'step4_p2g')
    p2g_gro = opj(p2g_path, prop['p2g_gro'])
    p2g_top = opj(p2g_path, prop['p2g_top'])
    p2g = pdb2gmx.Pdb2gmx512(scw_pdb, p2g_gro,
                             p2g_top, gmx_path=gmx_path).launch()

    # Define box dimensions
    # ec = editconf.Editconf512(prop['p2g_gro'], prop['box_gro'])
    # ec.launch()
    #
    # # Fill the box with water molecules
    # sol = solvate.Solvate512(prop['box_gro'], prop['sol_gro'], prop['top'])
    # sol.launch()
    #
    # # Add ions to neutralice the charge
    # ions_mdp = os.path.join(mdp_dir, prop['ions_mdp'])
    # gpp = grompp.Grompp512(ions_mdp, prop['sol_gro'], prop['top'],
    #                        prop['ions_tpr'])
    # gpp.launch()
    #
    # gio = genion.Genion512(prop['ions_tpr'], prop['ions_gro'], prop['top'])
    # gio.launch()
    #
    # # Energy minimization
    # gpp = grompp.Grompp512(prop['min_mdp'], prop['ions_gro'], prop['top'],
    #                        prop['min_tpr'])
    # gpp.launch()
    #
    # mdr = mdrun.Mdrun512(prop['min_tpr'], prop['min_trr'], prop['min_gro'],
    #                      prop['min_edr'])
    # mdr.launch()
    #
    # # Equilibration step 1/2 nvt (constant number of molecules, volume and temp)
    # gpp = grompp.Grompp512(prop['nvt_mdp'], prop['min_gro'],  prop['top'],
    #                        prop['nvt_tpr'])
    # gpp.launch()
    #
    # mdr = mdrun.Mdrun512(prop['nvt_tpr'], prop['nvt_gro'], prop['nvt_trr'],
    #                      prop['nvt_edr'], output_cpt_path=prop['nvt_cpt'])
    # mdr.launch()
    #
    # # Equilibration step 2/2 npt (constant number of molecules, pressure and temp)
    # gpp = grompp.Grompp512(prop['npt_mdp'], prop['nvt_gro'], prop['top'],
    #                        prop['npt_tpr'], cpt_path=prop['nvt_cpt'])
    # gpp.launch()
    #
    # mdr = mdrun.Mdrun512(prop['npt_tpr'],  prop['npt_gro'], prop['npt_trr'],
    #                      prop['npt_edr'], output_cpt_path=prop['npt_cpt'])
    # mdr.launch()
    #
    # # 1ns Molecular dynamics
    # gpp = grompp.Grompp512(prop['md_mdp'], prop['npt_gro'], prop['top'],
    #                        prop['md_tpr'],  cpt_path=prop['npt_cpt'])
    # gpp.launch()
    #
    # mdr = mdrun.Mdrun512(prop['md_tpr'], prop['md_gro'], prop['md_trr'],
    #                      prop['md_edr'], output_cpt_path=prop['md_cpt'])
    # mdr.launch()

    break
