#!/usr/bin/env python

"""Python wrapper for the GROMACS grompp module
"""
import os
import sys
import json
from os.path import join as opj
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu
import time

class Grompp(object):
    """Wrapper for the 5.1.2 version of the GROMACS grompp module.
    The GROMACS preprocessor module needs to be feeded with the input system
    and the molecular dynamics parameter file MDP, to create a portable binary
    run input file TPR.
    Args:
        input_gro_path (str): Path to the input GROMACS structure GRO file.
        input_top_zip_path (str): Path the input GROMACS topology TOP file.
        output_tpr_path (str): Path to the output portable binary run file TPR.
        input_cpt_path (str): Path to the input GROMACS checkpoint file CPT.
        input_mdp_path (str): Path to the input GROMACS parameter input file MDP.
        properties (dic):
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_gro_path, input_top_zip_path,
                 output_tpr_path, properties, input_cpt_path=None, **kwargs):

        self.input_gro_path = input_gro_path
        self.input_top_zip_path = input_top_zip_path
        self.output_tpr_path = output_tpr_path
        self.input_cpt_path = input_cpt_path
        self.input_mdp_path= properties.get('input_mdp_path', None)
        self.output_mdp_path= properties.get('output_mdp_path', 'generated.mdp')
        self.gmx_path = properties.get('gmx_path', None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)
        self.mdp = {k: str(v) for k, v in properties.get('mdp', None).items()}
        self.global_log= properties.get('global_log', None)
        self.nsteps=''
        self.dt=''


    def create_mdp(self):
        """Creates an MDP file using the properties file settings
        """

        mdp_list=[]
        mdp_file_path=fu.add_step_mutation_path_to_name(self.output_mdp_path, self.step, self.mutation)

        sim_type = self.mdp.get('type', 'minimization')
        minimization = (sim_type == 'minimization')
        nvt = (sim_type == 'nvt')
        npt = (sim_type == 'npt')
        free = (sim_type == 'free')
        index = (sim_type == 'index')
        md = (nvt or npt or free)
        mdp_list.append(";Type of MDP: " + sim_type)

        # Position restrain
        if not free:
            mdp_list.append("\n;Position restrain")
            mdp_list.append("Define = " + self.mdp.pop('define', '-DPOSRES'))

        # Run parameters
        mdp_list.append("\n;Run parameters")
        self.nsteps= self.mdp.pop('nsteps', '5000')
        mdp_list.append("nsteps = " + self.nsteps)
        if minimization:
            mdp_list.append("integrator = " + self.mdp.pop('integrator', 'steep'))
            mdp_list.append("emtol = " + self.mdp.pop('emtol', '1000.0'))
            mdp_list.append("emstep = " + self.mdp.pop('emstep', '0.01'))
        if md:
            mdp_list.append("integrator = " + self.mdp.pop('integrator', 'md'))
            self.dt=self.mdp.pop('dt', '0.002')
            mdp_list.append("dt = " + self.dt)

        # Output control
        if md:
            mdp_list.append("\n;Output control")
            if nvt or npt:
                mdp_list.append("nstxout = " + self.mdp.pop('nstxout',   '500'))
                mdp_list.append("nstvout = " + self.mdp.pop('nstvout',   '500'))
                mdp_list.append("nstenergy = " + self.mdp.pop('nstenergy', '500'))
                mdp_list.append("nstlog = " + self.mdp.pop('nstlog',    '500'))
                mdp_list.append("nstcalcenergy = " + self.mdp.pop('nstcalcenergy', '100'))
                mdp_list.append("nstcomm = " + self.mdp.pop('nstcomm', '100'))
                mdp_list.append("nstxout-compressed = " + self.mdp.pop('nstxout-compressed', '1000'))
                mdp_list.append("compressed-x-precision = " + self.mdp.pop('compressed-x-precision', '1000'))
                mdp_list.append("compressed-x-grps = " + self.mdp.pop('compressed-x-grps', 'System'))
            if free:
                mdp_list.append("nstcomm = " + self.mdp.pop('nstcomm', '100'))
                mdp_list.append("nstxout = " + self.mdp.pop('nstxout',   '5000'))
                mdp_list.append("nstvout = " + self.mdp.pop('nstvout',   '5000'))
                mdp_list.append("nstenergy = " + self.mdp.pop('nstenergy', '5000'))
                mdp_list.append("nstlog = " + self.mdp.pop('nstlog',    '5000'))
                mdp_list.append("nstcalcenergy = " + self.mdp.pop('nstcalcenergy', '100'))
                mdp_list.append("nstxout-compressed = " + self.mdp.pop('nstxout-compressed', '1000'))
                mdp_list.append("compressed-x-grps = " + self.mdp.pop('compressed-x-grps', 'System'))
                mdp_list.append("compressed-x-precision = " + self.mdp.pop('compressed-x-precision', '1000'))

        # Bond parameters
        if md:
            mdp_list.append("\n;Bond parameters")
            mdp_list.append("constraint_algorithm = " + self.mdp.pop('constraint_algorithm', 'lincs'))
            mdp_list.append("constraints = " + self.mdp.pop('constraints', 'all-bonds'))
            mdp_list.append("lincs_iter = " + self.mdp.pop('lincs_iter', '1'))
            mdp_list.append("lincs_order = " + self.mdp.pop('lincs_order', '4'))
            if nvt:
                mdp_list.append("continuation = " + self.mdp.pop('continuation', 'no'))
            if npt or free:
                mdp_list.append("continuation = " + self.mdp.pop('continuation', 'yes'))


        # Neighbour searching
        mdp_list.append("\n;Neighbour searching")
        mdp_list.append("cutoff-scheme = " + self.mdp.pop('cutoff-scheme', 'Verlet'))
        mdp_list.append("ns_type = " + self.mdp.pop('ns_type', 'grid'))
        mdp_list.append("rcoulomb = " + self.mdp.pop('rcoulomb', '1.0'))
        mdp_list.append("vdwtype = " + self.mdp.pop('vdwtype', 'cut-off'))
        mdp_list.append("rvdw = " + self.mdp.pop('rvdw', '1.0'))
        mdp_list.append("nstlist = " + self.mdp.pop('nstlist', '10'))
        mdp_list.append("rlist = " + self.mdp.pop('rlist', '1'))

        # Eletrostatics
        mdp_list.append("\n;Eletrostatics")
        mdp_list.append("coulombtype = " + self.mdp.pop('coulombtype', 'PME'))
        if md:
            mdp_list.append("pme_order = " + self.mdp.pop('pme_order', '4'))
            mdp_list.append("fourierspacing = " + self.mdp.pop('fourierspacing', '0.12'))
            mdp_list.append("fourier_nx = " + self.mdp.pop('fourier_nx', '0'))
            mdp_list.append("fourier_ny = " + self.mdp.pop('fourier_ny', '0'))
            mdp_list.append("fourier_nz = " + self.mdp.pop('fourier_nz', '0'))
            mdp_list.append("ewald_rtol = " + self.mdp.pop('ewald_rtol', '1e-5'))

        # Temperature coupling
        if md:
            mdp_list.append("\n;Temperature coupling")
            mdp_list.append("tcoupl = " + self.mdp.pop('tcoupl', 'V-rescale'))
            mdp_list.append("tc-grps = " + self.mdp.pop('tc-grps', 'Protein Non-Protein'))
            mdp_list.append("tau_t = " + self.mdp.pop('tau_t', '0.1	  0.1'))
            mdp_list.append("ref_t = " + self.mdp.pop('ref_t', '300 	  300'))

        # Pressure coupling
        if md:
            mdp_list.append("\n;Pressure coupling")
            if nvt:
                mdp_list.append("pcoupl = " + self.mdp.pop('pcoupl', 'no'))
            if npt or free:
                mdp_list.append("pcoupl = " + self.mdp.pop('pcoupl', 'Parrinello-Rahman'))
                mdp_list.append("pcoupltype = " + self.mdp.pop('pcoupltype', 'isotropic'))
                mdp_list.append("tau_p = " + self.mdp.pop('tau_p', '1.0'))
                mdp_list.append("ref_p = " + self.mdp.pop('ref_p', '1.0'))
                mdp_list.append("compressibility = " + self.mdp.pop('compressibility', '4.5e-5'))
                mdp_list.append("refcoord_scaling = " + self.mdp.pop('refcoord_scaling', 'com'))


        # Dispersion correction
        if md:
            mdp_list.append("\n;Dispersion correction")
            mdp_list.append("DispCorr = " + self.mdp.pop('DispCorr', 'EnerPres'))

        # Velocity generation
        if md:
            mdp_list.append("\n;Velocity generation")
            if nvt:
                mdp_list.append("gen_vel = " + self.mdp.pop('gen_vel', 'yes'))
                mdp_list.append("gen_temp = " + self.mdp.pop('gen_temp', '300'))
                mdp_list.append("gen_seed = " + self.mdp.pop('gen_seed', '-1'))
            if npt or free:
                mdp_list.append("gen_vel = " + self.mdp.pop('gen_vel', 'no'))

        #Periodic boundary conditions
        mdp_list.append("\n;Periodic boundary conditions")
        mdp_list.append("pbc = " + self.mdp.pop('pbc', 'xyz'))

        if index:
            mdp_list =[";This mdp file has been created by the pymdsetup.gromacs_wrapper.grompp.create_mdp()"]

        mdp_list.insert(0, ";This mdp file has been created by the pymdsetup.gromacs_wrapper.grompp.create_mdp()")

        # Adding the rest of parameters in the config file to the MDP file
        for k, v in self.mdp.iteritems():
            if k != 'type':
                mdp_list.append(str(k) + ' = '+str(v))

        with open(mdp_file_path, 'w') as mdp:
            for line in mdp_list:
                mdp.write(line + '\n')

        return mdp_file_path

    def launch(self):
        """Launches the execution of the GROMACS grompp module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        mdp_file_path = self.create_mdp() if self.input_mdp_path is None else self.input_mdp_path
        out_log.info("Creating mdp path: "+mdp_file_path)
        if self.global_log is not None:
            md = self.mdp.get('type', 'minimization')
            if md != 'index' and md != 'free':
                self.global_log.info(22*' '+'Will run a '+md+' md of ' + str(self.nsteps) +' steps')
            elif md == 'index':
                self.global_log.info(22*' '+'Will create a TPR to be used as structure file')
            else:
                self.global_log.info(22*' '+'Will run a '+md+' md of ' + fu.human_readable_time(int(self.nsteps)*float(self.dt)))

        # Unzip topology in de directory of the output_tpr_path and get the
        # topology path
        out_log.info("Calling unzip_top")
        topology_path = fu.unzip_top(self.input_top_zip_path, out_log=out_log, dest_dir=self.mutation+'_'+self.step+'_top')
        out_log.info('After unzip_top')
        out_log.info('')
        out_log.info('Grompp after decompressing topology_path: '+topology_path)

        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'grompp', '-f', mdp_file_path,
               '-c', self.input_gro_path,
               '-p', topology_path,
               '-o', self.output_tpr_path,
               '-maxwarn','1000']

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        if self.input_cpt_path is not None:
            cmd.append('-t')
            cmd.append(self.input_cpt_path)
        if self.output_mdp_path is not None:
            cmd.append('-po')
            cmd.append(self.output_mdp_path)

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        return command.launch()

#Creating a main function to be compatible with CWL
def main():
    if len(sys.argv) < 9:
        sys.argv.append(None)
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Grompp(input_gro_path = sys.argv[4],
           input_top_zip_path = sys.argv[5],
           input_mdp_path = sys.argv[6],
           output_tpr_path = sys.argv[7],
           input_cpt_path = sys.argv[8],
           properties=prop).launch()

if __name__ == '__main__':
    main()
