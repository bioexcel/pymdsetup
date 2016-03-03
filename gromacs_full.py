# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb

@author: pau
"""

import settings
import requests
import pdb2gmx
import re
import editconf
import solvate
import grompp
import genion
import mdrun

prop = settings.YamlReader().properties

pdb_path = "structure.pdb"
pdb_code = "1NAG"

# Get PDB file from the MMB API without solvent or ligands
url = "mmb.irbbarcelona.org/api/pdb/"+pdb_code.lower()+"/coords/?group=ATOM"
pdb_string = requests.get(url)
with open(pdb_path, 'w') as pdb_file:
    pdb_file.write(pdb_string)

# Create gromacs topology 
p2g = pdb2gmx.Pdb2gmx512(pdb_path, prop['p2g_gro'], prop['p2g_log'])
p2g.launch()

#Get the total charge of the molecule
with open(prop['p2g_log'], 'w') as p2g_log_file:
    out = p2g_log_file.read()
    charge = float(
           re.search(r'Total charge ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)',
                     out, re.MULTILINE))

# Define box dimensions
ec = editconf.Editconf512(prop['p2g_gro'], prop['box_gro'])
ec.launch()

# Fill the box with water molecules
sol = solvate.Solvate512(prop['box_gro'], prop['sol_gro'], prop['top'])
sol.launch()

# Add ions to neutralice the charge
gpp = grompp.Grompp512(prop['ions_mdp'], prop['sol_gro'], prop['top'], 
                       prop['ions_tpr'])
gpp.launch()

gio = genion.Genion512(prop['ions_tpr'], prop['ions_gro'], prop['top'], charge)
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

mdr = mdrun.Mdrun512(prop['nvt_tpr'], prop['nvt_trr'], prop['nvt_gro'],
                     prop['nvt_edr'], prop['nvt_cpt'])

# 1ns Molecular dynamics
gpp = grompp.Grompp512(prop['md_mdp'], prop['npt_gro'], prop['npt_cpt'],
                       prop['top'], prop['md_tpr'])
gpp.launch()

mdr = mdrun.Mdrun512(prop['md_tpr'], prop['md_trr'], prop['md_gro'],
                     prop['md_edr'], prop['md_cpt'])

 