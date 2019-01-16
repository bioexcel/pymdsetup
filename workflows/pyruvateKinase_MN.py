import os
import sys
import time
import traceback
import tools.file_utils as fu
import configuration.settings as settings
import gromacs_wrapper.pdb2gmx as pdb2gmx
import gromacs_wrapper.grompp as grompp
import scwrl_wrapper.scwrl as scwrl
import gromacs_wrapper.solvate as solvate
import gromacs_wrapper.editconf as editconf
import gromacs_wrapper.genion as genion
import gromacs_wrapper.mdrun as mdrun
import gromacs_wrapper.make_ndx as make_ndx
import gromacs_wrapper.genrestr as genrestr
import mmb_api.pdb as pdb
import mmb_api.uniprot as uniprot
import gromacs_wrapper.rms as rms
import gnuplot_wrapper.gnuplot as gnuplot
import gromacs_extra.ndx2resttop as ndx2resttop
from pycompss.api.parameter import *
from pycompss.api.task import task
from pycompss.api.constraint import constraint
from pycompss.api.mpi import mpi
from os.path import join as opj
from pycompss.api.api import compss_barrier

def main():
    from pycompss.api.api import compss_open, compss_barrier
    start_time = time.time()
    yaml_path=sys.argv[1]
    system=sys.argv[2]
    mut_start=int(sys.argv[3])
    mut_end=int(sys.argv[4])

    conf = settings.YamlReader(yaml_path, system)
    workflow_path = conf.properties[system]['workflow_path']+'_'+str(mut_start)+'_'+str(mut_end)+'mut'
    conf.properties[system]['workflow_path']=workflow_path
    fu.create_dir(os.path.abspath(workflow_path))
    out_log, _ = fu.get_logs(path=workflow_path, console=True, level='DEBUG')
    paths_glob = conf.get_paths_dic()
    prop_glob = conf.get_prop_dic()

    out_log.info('')
    out_log.info('_______GROMACS FULL WORKFLOW_______')
    out_log.info('')

    out_log.info("Command Executed:")
    out_log.info(" ".join(sys.argv))
    out_log.info('Workflow_path: '+workflow_path)
    out_log.info('Config File: '+yaml_path)
    out_log.info('System: '+system)

    out_log.info('')
    out_log.info( 'step1:  mmbpdb -- Get PDB')
    structure = conf.properties[system].get('initial_structure_pdb_path', None)
    if structure is None or not os.path.isfile(structure):
        out_log.info( 22*' '+'Selected PDB code: ' + prop_glob['step1_mmbpdb']['pdb_code'])
        fu.create_dir(prop_glob['step1_mmbpdb']['path'])
        pdb.MmbPdb().get_pdb(prop_glob['step1_mmbpdb']['pdb_code'], paths_glob['step1_mmbpdb']['output_pdb_path'])
        structure = paths_glob['step1_mmbpdb']['output_pdb_path']
    else:
        out_log.info( 22*' '+'Selected PDB structure: ' + structure)

    out_log.info( 'step2:  mmbuniprot -- Get mutations')
    mutations = conf.properties.get('input_mapped_mutations_list', None)
    mutations = [m.strip() for m in conf.properties.get('input_mapped_mutations_list').split(',')]
    mutations = mutations[mut_start:mut_end]
    n_mutations = len(mutations)
    out_log.info( 22*' '+'Mutations_start: ' + str(mut_start))
    out_log.info( 22*' '+'Mutations_end: ' + str(mut_end))
    out_log.info( 22*' '+'Number of mutations in list: ' + str(n_mutations))
    mutations_counter=1 
    rms_list = []
    for mut in mutations:
        mut = mut if not mut.startswith('*') else mut.replace('*', 'ALL')
        paths = conf.get_paths_dic(mut)
        prop = conf.get_prop_dic(mut)

        out_log.info('')
        out_log.info('-------------------------')
        out_log.info(str(mutations_counter) + '/' + str(n_mutations) + ' ' + mut)
        mutations_counter += 1 
        out_log.info('-------------------------')
        out_log.info('')

        out_log.info('step3: scw ---------- Model mutation')
        fu.create_dir(prop['step3_scw']['path'])
        paths['step3_scw']['input_pdb_path']=structure
        out_log.debug('Paths:')
        out_log.debug(str(paths['step3_scw']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step3_scw'])+'\n')
        scwrl_pc(properties=prop['step3_scw'], **paths['step3_scw'])

        out_log.info('step4: p2g ---------- Create gromacs topology')
        fu.create_dir(prop['step4_p2g']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step4_p2g']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step4_p2g'])+'\n')
        pdb2gmx_pc(properties=prop['step4_p2g'], **paths['step4_p2g'])

        out_log.info('step5: ec ----------- Define box dimensions')
        fu.create_dir(prop['step5_ec']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step5_ec']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step5_ec'])+'\n')
        editconf_pc(properties=prop['step5_ec'], **paths['step5_ec'])

        out_log.info('step6: sol ---------- Fill the box with water molecules')
        fu.create_dir(prop['step6_sol']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step6_sol']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step6_sol'])+'\n')
        solvate_pc(properties=prop['step6_sol'], **paths['step6_sol'])

        out_log.info('step7: gppions ------ Preprocessing: Adding monoatomic ions')
        fu.create_dir(prop['step7_gppions']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step7_gppions']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step7_gppions'])+'\n')
        grompp_pc(properties=prop['step7_gppions'], **paths['step7_gppions'])

        out_log.info('step8: gio ---------- Running: Adding monoatomic ions')
        fu.create_dir(prop['step8_gio']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step8_gio']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step8_gio'])+'\n')
        genion_pc(properties=prop['step8_gio'], **paths['step8_gio'])

        out_log.info('Step9: gppndx ------- Preprocessing index creation')
        fu.create_dir(prop['step9_gppndx']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step9_gppndx']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step9_gppndx'])+'\n')
        grompp_pc(properties=prop['step9_gppndx'], **paths['step9_gppndx'])

        out_log.info('Step10: make_ndx ---- Create restrain index')
        fu.create_dir(prop['step10_make_ndx']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step10_make_ndx']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step10_make_ndx'])+'\n')
        make_ndx_pc(properties=prop['step10_make_ndx'], **paths['step10_make_ndx'])

        out_log.info('Step11: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step11_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step11_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step11_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step11_ndx2resttop'], **paths['step11_ndx2resttop'])

        out_log.info('step12: gppresmin --- Preprocessing: Mutated residue minimization')
        fu.create_dir(prop['step12_gppresmin']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step12_gppresmin']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step12_gppresmin'])+'\n')
        grompp_pc(properties=prop['step12_gppresmin'], **paths['step12_gppresmin'])

        out_log.info('step13: mdresmin ---- Running: Mutated residue minimization')
        fu.create_dir(prop['step13_mdresmin']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step13_mdresmin']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step13_mdresmin'])+'\n')
        pa = paths['step13_mdresmin']
        pr = prop['step13_mdresmin']
        mdrun_pc(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('Step14: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step14_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step14_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step14_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step14_ndx2resttop'], **paths['step14_ndx2resttop'])

        out_log.info('step15: gppmin ------ Preprocessing: minimization')
        fu.create_dir(prop['step15_gppmin']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step15_gppmin']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step15_gppmin'])+'\n')
        grompp_pc(properties=prop['step15_gppmin'], **paths['step15_gppmin'])

        out_log.info('step16: mdmin ------- Running: minimization')
        fu.create_dir(prop['step16_mdmin']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step16_mdmin']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step16_mdmin'])+'\n')
        pa = paths['step16_mdmin']
        pr = prop['step16_mdmin']
        mdrun_pc(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('Step17: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step17_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step17_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step17_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step17_ndx2resttop'], **paths['step17_ndx2resttop'])

        out_log.info('step18: gppsa ------- Preprocessing: simulated annealing')
        fu.create_dir(prop['step18_gppsa']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step18_gppsa']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step18_gppsa'])+'\n')
        grompp_pc(properties=prop['step18_gppsa'], **paths['step18_gppsa'])

        out_log.info('step19: mdsa -------- Running: simulated annealing')
        fu.create_dir(prop['step19_mdsa']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step19_mdsa']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step19_mdsa'])+'\n')
        pa = paths['step19_mdsa']
        pr = prop['step19_mdsa']
        mdrun_pc_cpt(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('step20: gppnvt_1000 - Preprocessing: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step20_gppnvt_1000']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step20_gppnvt_1000']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step20_gppnvt_1000'])+'\n')
        grompp_pc_cpt(properties=prop['step20_gppnvt_1000'], **paths['step20_gppnvt_1000'])

        out_log.info('step21: mdnvt_1000 -- Running: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step21_mdnvt_1000']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step21_mdnvt_1000']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step21_mdnvt_1000'])+'\n')
        pa = paths['step21_mdnvt_1000']
        pr = prop['step21_mdnvt_1000']
        mdrun_pc_cpt(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('Step22: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step22_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step22_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step22_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step22_ndx2resttop'], **paths['step22_ndx2resttop'])

        out_log.info('step23: gppnvt_800 -- Preprocessing: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step23_gppnvt_800']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step23_gppnvt_800']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step23_gppnvt_800'])+'\n')
        grompp_pc_cpt(properties=prop['step23_gppnvt_800'], **paths['step23_gppnvt_800'])

        out_log.info('step24: mdnvt_800 --- Running: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step24_mdnvt_800']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step24_mdnvt_800']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step24_mdnvt_800'])+'\n')
        pa = paths['step24_mdnvt_800']
        pr = prop['step24_mdnvt_800']
        mdrun_pc_cpt(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('Step25: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step25_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step25_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step25_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step25_ndx2resttop'], **paths['step25_ndx2resttop'])

        out_log.info('step26: gppnpt_500 -- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step26_gppnpt_500']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step26_gppnpt_500']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step26_gppnpt_500'])+'\n')
        grompp_pc_cpt(properties=prop['step26_gppnpt_500'], **paths['step26_gppnpt_500'])

        out_log.info('step27: mdnpt_500 --- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step27_mdnpt_500']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step27_mdnpt_500']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step27_mdnpt_500'])+'\n')
        pa = paths['step27_mdnpt_500']
        pr = prop['step27_mdnpt_500']
        mdrun_pc_cpt(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('Step28: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step28_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step28_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step28_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step28_ndx2resttop'], **paths['step28_ndx2resttop'])

        out_log.info('step29: gppnpt_300 -- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step29_gppnpt_300']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step29_gppnpt_300']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step29_gppnpt_300'])+'\n')
        grompp_pc_cpt(properties=prop['step29_gppnpt_300'], **paths['step29_gppnpt_300'])

        out_log.info('step30: mdnpt_300 --- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step30_mdnpt_300']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step30_mdnpt_300']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step30_mdnpt_300'])+'\n')
        pa = paths['step30_mdnpt_300']
        pr = prop['step30_mdnpt_300']
        mdrun_pc_cpt(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('Step31: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step31_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step31_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step31_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step31_ndx2resttop'], **paths['step31_ndx2resttop'])

        out_log.info('step32: gppnpt_200 -- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step32_gppnpt_200']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step32_gppnpt_200']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step32_gppnpt_200'])+'\n')
        grompp_pc_cpt(properties=prop['step32_gppnpt_200'], **paths['step32_gppnpt_200'])

        out_log.info('step33: mdnpt_200 --- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step33_mdnpt_200']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step33_mdnpt_200']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step33_mdnpt_200'])+'\n')
        pa = paths['step33_mdnpt_200']
        pr = prop['step33_mdnpt_200']
        mdrun_pc_cpt(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('Step34: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step34_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step34_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step34_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step34_ndx2resttop'], **paths['step34_ndx2resttop'])

        out_log.info('step35: gppnpt_100 -- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step35_gppnpt_100']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step35_gppnpt_100']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step35_gppnpt_100'])+'\n')
        grompp_pc_cpt(properties=prop['step35_gppnpt_100'], **paths['step35_gppnpt_100'])

        out_log.info('step36: mdnpt_100 --- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step36_mdnpt_100']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step36_mdnpt_100']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step36_mdnpt_100'])+'\n')
        pa = paths['step36_mdnpt_100']
        pr = prop['step36_mdnpt_100']
        mdrun_pc_cpt(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('Step37: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step37_ndx2resttop']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step37_ndx2resttop']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step37_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step37_ndx2resttop'], **paths['step37_ndx2resttop'])

        out_log.info('step38: gppnpt ------ Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step38_gppnpt']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step38_gppnpt']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step38_gppnpt'])+'\n')
        grompp_pc_cpt(properties=prop['step38_gppnpt'], **paths['step38_gppnpt'])

        out_log.info('step39: mdnpt ------- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step39_mdnpt']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step39_mdnpt']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step39_mdnpt'])+'\n')
        pa = paths['step39_mdnpt']
        pr = prop['step39_mdnpt']
        mdrun_pc_cpt(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_trr_path=pr["output_trr_path"], output_xtc_path=pr["output_xtc_path"], output_edr_path=pr["output_edr_path"], output_log_path=pa["output_log_path"])

        out_log.info('step40: gppmd ------- Preprocessing: Free Molecular dynamics')
        fu.create_dir(prop['step40_gppmd']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step40_gppmd']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step40_gppmd'])+'\n')
        grompp_pc_cpt(properties=prop['step40_gppmd'], **paths['step40_gppmd'])

        out_log.info('step41: md ---------- Running: Free Molecular dynamics')
        fu.create_dir(prop['step41_md']['path'])
        out_log.debug('Paths:')
        out_log.debug(str(paths['step41_md']))
        out_log.debug('Properties:')
        out_log.debug(str(prop['step41_md'])+'\n')
        pa = paths['step41_md']
        pr = prop['step41_md']
        mdrun_pc_all(input_tpr_path=pa["input_tpr_path"], output_gro_path=pa["output_gro_path"], output_cpt_path=pa["output_cpt_path"], output_xtc_path=pa["output_xtc_path"], output_trr_path=pa["output_trr_path"], output_edr_path=pa["output_edr_path"], output_log_path=pa["output_log_path"])

    compss_barrier()

    elapsed_time = time.time() - start_time
    out_log.info('')
    out_log.info('')
    out_log.info('Execution sucessful: ')
    out_log.info('  Workflow_path: '+workflow_path)
    out_log.info('  Config File: '+yaml_path)
    out_log.info('  System: '+system)
    # TO DO: Hardcoded check the number of nodes master/execution dynamically
    out_log.info('')
    out_log.info('Elapsed time: '+str(elapsed_time/60)+' minutes')
    out_log.info('')

############################## PyCOMPSs functions #############################
#MareNostrum4
computing_units = "48"
computing_nodes = 4

def write_failed_output(filename):
    with open(filename, 'w') as f:
        f.write('Failed\n')

@constraint(ComputingUnits=computing_units)
@mpi(runner="mpirun", binary="gmx_mpi", computingNodes=computing_nodes)
@task(input_tpr_path=FILE_IN, output_gro_path=FILE_OUT, output_log_path=FILE_OUT)
def mdrun_pc(mdrun="mdrun", s="-s",input_tpr_path="", c="-c",output_gro_path="", o="-o",output_trr_path="", x="-x",output_xtc_path="", e="-e", output_edr_path="", g="-g",output_log_path=""):
    pass

@constraint(ComputingUnits=computing_units)
@mpi(runner="mpirun", binary="gmx_mpi", computingNodes=computing_nodes)
@task(input_tpr_path=FILE_IN, output_gro_path=FILE_OUT, output_cpt_path=FILE_OUT, output_log_path=FILE_OUT)
def mdrun_pc_cpt(mdrun="mdrun", s="-s",input_tpr_path="", c="-c",output_gro_path="", o="-o",output_trr_path="", x="-x",output_xtc_path="", e="-e", output_edr_path="", cpo="-cpo",output_cpt_path="", g="-g",output_log_path=""):
    pass


@constraint(ComputingUnits=computing_units)
@mpi(runner="mpirun", binary="gmx_mpi", computingNodes=computing_nodes)
@task(input_tpr_path=FILE_IN, output_gro_path=FILE_OUT, output_cpt_path=FILE_OUT, output_trr_path=FILE_OUT, output_xtc_path=FILE_OUT, output_edr_path=FILE_OUT, output_log_path=FILE_OUT)
def mdrun_pc_all(mdrun="mdrun", s="-s",input_tpr_path="", c="-c",output_gro_path="", o="-o",output_trr_path="", x="-x",output_xtc_path="", e="-e", output_edr_path="", cpo="-cpo",output_cpt_path="", g="-g",output_log_path=""):
    pass

@task(input_pdb_path=FILE_IN, output_pdb_path=FILE_OUT)
def scwrl_pc(input_pdb_path, output_pdb_path, properties, **kwargs):
    try:
        scwrl.Scwrl4(input_pdb_path=input_pdb_path, output_pdb_path=output_pdb_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_pdb_path)

@task(input_structure_pdb_path=FILE_IN, output_gro_path=FILE_OUT, output_top_zip_path=FILE_OUT)
def pdb2gmx_pc(input_structure_pdb_path, output_gro_path, output_top_zip_path, properties, **kwargs):
    try:
        pdb2gmx.Pdb2gmx(input_structure_pdb_path=input_structure_pdb_path, output_gro_path=output_gro_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_gro_path)
        write_failed_output(output_top_zip_path)

@task(input_gro_path=FILE_IN, output_gro_path=FILE_OUT)
def editconf_pc(input_gro_path, output_gro_path, properties, **kwargs):
    try:
        editconf.Editconf(input_gro_path=input_gro_path, output_gro_path=output_gro_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_gro_path)

@task(input_solute_gro_path=FILE_IN, output_gro_path=FILE_OUT, input_top_zip_path=FILE_IN, output_top_zip_path=FILE_OUT)
def solvate_pc(input_solute_gro_path, output_gro_path, input_top_zip_path, output_top_zip_path, properties, **kwargs):
    try:
        solvate.Solvate(input_solute_gro_path=input_solute_gro_path, output_gro_path=output_gro_path, input_top_zip_path=input_top_zip_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_gro_path)
        write_failed_output(output_top_zip_path)

@task(input_gro_path=FILE_IN, input_top_zip_path=FILE_IN, output_tpr_path=FILE_OUT,  input_cpt_path=FILE_IN)
def grompp_pc_cpt(input_gro_path, input_top_zip_path, output_tpr_path, input_cpt_path, properties, **kwargs):
    try:
        grompp.Grompp(input_gro_path=input_gro_path, input_top_zip_path=input_top_zip_path, output_tpr_path=output_tpr_path, input_cpt_path=input_cpt_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_tpr_path)

@task(input_gro_path=FILE_IN, input_top_zip_path=FILE_IN, output_tpr_path=FILE_OUT)
def grompp_pc(input_gro_path, input_top_zip_path, output_tpr_path, properties, **kwargs):
    try:
        grompp.Grompp(input_gro_path=input_gro_path, input_top_zip_path=input_top_zip_path, output_tpr_path=output_tpr_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_tpr_path)

@task(input_tpr_path=FILE_IN, output_gro_path=FILE_OUT, input_top_zip_path=FILE_IN, output_top_zip_path=FILE_OUT)
def genion_pc(input_tpr_path, output_gro_path, input_top_zip_path, output_top_zip_path, properties, **kwargs):
    try:
        genion.Genion(input_tpr_path=input_tpr_path, output_gro_path=output_gro_path, input_top_zip_path=input_top_zip_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_gro_path)
        write_failed_output(output_top_zip_path)

@task(input_gro_path=FILE_IN, input_xtc_path=FILE_IN, output_xvg_path=FILE_OUT, returns=dict)
def rms_pc(input_gro_path, input_xtc_path, output_xvg_path, properties, **kwargs):
    try:
        return rms.Rms(input_gro_path=input_gro_path, input_xtc_path=input_xtc_path, output_xvg_path=output_xvg_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_xvg_path)

@task(output_png_path=FILE_OUT)
def gnuplot_pc(input_xvg_path_dict, output_png_path, properties, **kwargs):
    try:
        gnuplot.Gnuplot(input_xvg_path_dict=input_xvg_path_dict, output_png_path=output_png_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_png_path)

@task(input_ndx_path=FILE_IN, input_top_zip_path=FILE_IN, output_top_zip_path=FILE_OUT)
def ndx2resttop_pc(input_ndx_path, input_top_zip_path, output_top_zip_path, properties, **kwargs):
    try:
        ndx2resttop.Ndx2resttop(input_ndx_path=input_ndx_path, input_top_zip_path=input_top_zip_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_top_zip_path)

@task(input_structure_path=FILE_IN, output_ndx_path=FILE_OUT)
def make_ndx_pc(input_structure_path, output_ndx_path, properties, **kwargs):
    try:
        make_ndx.MakeNdx(input_structure_path=input_structure_path, output_ndx_path=output_ndx_path, properties=properties, **kwargs).launch()
    except Exception:
        traceback.print_exc()
        write_failed_output(output_ndx_path)


if __name__ == '__main__':
    main()
