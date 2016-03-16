# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb

@author: pau
"""

import settings
import requests
import os
import pdb2gmx
import editconf
import solvate
import grompp
import genion
import mdrun

prop = settings.YamlReader().properties

pdb_path = "structure.pdb"
pdb_code = "1NAJ"
filter = "filter=/1"


mdp_dir = os.path.join(os.path.dirname(__file__), 'mdp')

# Get PDB file from the MMB API without solvent or ligands
url = "mmb.irbbarcelona.org/api/pdb/"+pdb_code.lower()+"/coords/?"+filter
pdb_string = requests.get(url)
with open(pdb_path, 'w') as pdb_file:
    pdb_file.write(pdb_string)

# Create gromacs topology
p2g = pdb2gmx.Pdb2gmx512(pdb_path, prop['p2g_gro'])
p2g.launch()

# Define box dimensions
ec = editconf.Editconf512(prop['p2g_gro'], prop['box_gro'])
ec.launch()

# Fill the box with water molecules
sol = solvate.Solvate512(prop['box_gro'], prop['sol_gro'], prop['top'])
sol.launch()

# Add ions to neutralice the charge
ions_mdp = os.path.join(mdp_dir, prop['ions_mdp'])
gpp = grompp.Grompp512(ions_mdp, prop['sol_gro'], prop['top'],
                       prop['ions_tpr'])
gpp.launch()

gio = genion.Genion512(prop['ions_tpr'], prop['ions_gro'], prop['top'])
gio.launch()

# Energy minimization
gpp = grompp.Grompp512(prop['min_mdp'], prop['ions_gro'], prop['top'],
                       prop['min_tpr'])
gpp.launch()

mdr = mdrun.Mdrun512(prop['min_tpr'], prop['min_trr'], prop['min_gro'],
                     prop['min_edr'])
mdr.launch()

# Equilibration step 1/2 nvt (constant number of molecules, volume and temp)
gpp = grompp.Grompp512(prop['nvt_mdp'], prop['min_gro'],  prop['top'],
                       prop['nvt_tpr'])
gpp.launch()

mdr = mdrun.Mdrun512(prop['nvt_tpr'], prop['nvt_gro'], prop['nvt_trr'],
                     prop['nvt_edr'], output_cpt_path=prop['nvt_cpt'])
mdr.launch()

# Equilibration step 2/2 nvt (constant number of molecules, pressure and temp)
gpp = grompp.Grompp512(prop['npt_mdp'], prop['nvt_gro'], prop['top'],
                       prop['npt_tpr'], cpt_path=prop['nvt_cpt'])
gpp.launch()

mdr = mdrun.Mdrun512(prop['npt_tpr'],  prop['npt_gro'], prop['npt_trr'],
                     prop['npt_edr'], output_cpt_path=prop['npt_cpt'])
mdr.launch()

# 1ns Molecular dynamics
gpp = grompp.Grompp512(prop['md_mdp'], prop['npt_gro'], prop['top'],
                       prop['md_tpr'],  cpt_path=prop['npt_cpt'])
gpp.launch()

mdr = mdrun.Mdrun512(prop['md_tpr'], prop['md_gro'], prop['md_trr'],
                     prop['md_edr'], output_cpt_path=prop['md_cpt'])
mdr.launch()
