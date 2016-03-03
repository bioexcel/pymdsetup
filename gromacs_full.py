# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb

@author: pau
"""

import settings
import requests
import pdb2gmx
import re


prop = settings.YamlReader().properties

pdb_path = "structure.pdb"
pdb_code = "1NAG"

# Get PDB file from the MMB API without solvent or ligands
url = "mmb.irbbarcelona.org/api/pdb/"+pdb_code.lower()+"/coords/?group=ATOM"
pdb_string = requests.get(url)
with open(pdb_path, 'w') as pdb_file:
    pdb_file.write(pdb_string)

# Create gromacs topology 
p2g = pdb2gmx.Pdb2gmx512(pdb_path, prop['p2g_gro_path'], prop['p2g_log_path'])
p2g.launch()

#Get the total charge of the molecule
with open(prop['p2g_log_path'], 'w') as p2g_log_file:
    out = p2g_log_file.read()
    charge = float(
           re.search(r'Total charge ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)',
                     out, re.MULTILINE))

# Define box dimensions
ec = editconf.Editconf512(prop['p2g_gro_path'], prop['ec_gro_box_path'])
ec.launch()

# Fill the box with water molecules
sol = solvate.Solvate512(prop['ec_gro_box_path'], prop['sol_gro_sol_path'],
                         prop['sol_top_sol_path'])
sol.launch()

# Add ions to neutralice the charge
gpp = grompp.Grompp512(prop['gpp_mdp_ions_path'], prop['sol_gro_sol_path'],
                       prop['sol_top_sol_path'], prop['gpp_tpr_ions_path'])
gpp.launch()

gio = genion.Genion512(prop['gpp_tpr_ions_path'], prop['gio_gro_ions_path'],
                       prop['sol_top_sol_path'], charge)
gio.launch()

# Energy minimization
gpp = grompp.Grompp512(prop['gpp_mdp_min_path'], prop['gio_gro_ions_path'],
                       prop['sol_top_sol_path'], prop['gpp_tpr_min_path'])
gpp.launch()

mdr = mdrun.Mdrun512(prop)

# Equilibration step 1/2 nvt (constant number of molecules, volume and temp)
gpp = grompp.Grompp512()

# 