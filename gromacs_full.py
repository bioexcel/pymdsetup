# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb

@author: pau
"""

import requests
import pdb2gmx
import re

pdb_path = "structure.pdb"
pdb_code = "1NAG"

# Get PDB file from the MMB API without solvent or ligands
url = "mmb.irbbarcelona.org/api/pdb/"+pdb_code.lower()+"/coords/?group=ATOM"
pdb_string = requests.get(url)
with open(pdb_path, 'w') as pdb_file:
    pdb_file.write(pdb_string)

# Create gromacs topology
gro_path = "structure.gro"
p2g_log = "p2g.log"
p2g = pdb2gmx.Pdb2gmx512(pdb_path, gro_path, p2g_log)
p2g.launch()

#Get the total charge of the molecule
with open(p2g_log, 'w') as p2g_log_file:
    out = p2g_log_file.read()
    charge = float(
           re.search(r'Total charge ([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)',
                     out, re.MULTILINE))

# Define box dimensions
gro_box_path = "box.gro"
ec = editconf.Editconf512(gro_path, gro_box_path)
ec.launch()

# Fill the box with water molecules
gro_solv_path = "solv.gro"
topology = "topol.top"
solv = solvate.Solvate512(gro_box_path, gro_solv_path, topology)
solv.launch()

# Add ions to neutralice the charge


# 