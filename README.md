# pymdsetup

### Introduction
Pymdsetup is a python module to setup systems to run a molecular
dynamics simulation.

### Installation
1. Download & Install Anaconda5

        #!bash
        wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda2-2.5.0-Linux-x86_64.sh
        bash Anaconda2-2.5.0-Linux-x86_64.sh

2. Create an Anaconda environment

        #!bash
        conda create --name

### GROMACS installation
1. Download Gromacs package v.5.1.2 (February 2016)

        #!bash
        wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-5.1.2.tar.gz
        mv gromacs-5.1.2.tar.gz $HOME/soft/gromacs/
        cd $HOME/soft/gromacs/

2. Extract package

        #!bash
        tar xzvf gromacs-5.1.2.tar.gz
        rm -rf gromacs-5.1.2.tar.gz
        cd gromacs-5.1.2/

3. Build from source

        #!bash
        mkdir build
        cd build/
        cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON
        make
        make check
        sudo make install
        source /usr/local/gromacs/bin/GMXRC

### GROMACS not automated setup tutorial
(source: http://www.bevanlab.biochem.vt.edu/Pages/Personal/justin/gmx-tutorials/lysozyme/01_pdb2gmx.html)

1. Download the Lysozyme PDB structure

        #!bash
        curl mmb.irbbarcelona.org/api/pdb/1aki/coords > 1AKI.pdb

2. Remove crystal water molecules

        #!bash
        sed -i.bak '/HOH/d' ./1AKI.pdb

3. Creating Gromacs topology from the PDB file

        #!bash
        gmx pdb2gmx -f 1AKI.pdb -o 1AKI_processed.gro -water spce -ff oplsaa

4. Define the box dimensions

        #!bash
        gmx editconf -f 1AKI_processed.gro -o 1AKI_newbox.gro -c -d 1.0 -bt cubic

5. Fill the box with water molecules

        #!bash
        gmx solvate -cp 1AKI_newbox.gro -cs spc216.gro -o 1AKI_solv.gro -p topol.top

6. Add ions to neutralice the charge

        #!bash
        echo "; ions.mdp - used as input into grompp to generate ions.tpr
        ; Parameters describing what to do, when to stop and what to save
        integrator  = steep     ; Algorithm (steep = steepest descent minimization)
        emtol       = 1000.0    ; Stop minimization when the maximum force < 1000.0 kJ/mol/nm
        emstep      = 0.01      ; Energy step size
        nsteps      = 50000     ; Maximum number of (minimization) steps to perform

        ; Parameters describing how to find the neighbors of each atom and how to calculate the interactions
        nstlist         = 1         ; Frequency to update the neighbor list and long range forces
        cutoff-scheme   = Verlet
        ns_type         = grid      ; Method to determine neighbor list (simple, grid)
        coulombtype     = PME       ; Treatment of long range electrostatic
        interactions
        rcoulomb        = 1.0       ; Short-range electrostatic cut-off
        rvdw            = 1.0       ; Short-range Van der Waals cut-off
        pbc             = xyz       ; Periodic Boundary Conditions (yes/no)" > ions.mdp

        gmx grompp -f ions.mdp -c 1AKI_solv.gro -p topol.top -o ions.tpr

        echo "SOL" | gmx genion -s ions.tpr -o 1AKI_solv_ions.gro -p topol.top -pname NA -nname CL -nn 8

9. Energy minimization

        #!bash
        echo "; minim.mdp - used as input into grompp to generate em.tpr
        integrator  = steep     ; Algorithm (steep = steepest descent minimization)
        emtol       = 1000.0    ; Stop minimization when the maximum force < 1000.0
        kJ/mol/nm
        emstep      = 0.01      ; Energy step size
        nsteps      = 50000     ; Maximum number of (minimization) steps to perform

        ; Parameters describing how to find the neighbors of each atom and how to calculate the in
        nstlist         = 1         ; Frequency to update the neighbor list and long
        range forces
        cutoff-scheme   = Verlet
        ns_type         = grid      ; Method to determine neighbor list (simple, grid)
        coulombtype     = PME       ; Treatment of long range electrostatic interactions
        rcoulomb        = 1.0       ; Short-range electrostatic cut-off
        rvdw            = 1.0       ; Short-range Van der Waals cut-off
        pbc             = xyz       ; Periodic Boundary Conditions (yes/no)" > minim.mdp

        gmx grompp -f minim.mdp -c 1AKI_solv_ions.gro -p topol.top -o minim.tpr

        gmx mdrun -s minim.tpr -o minim.trr  -c minim.gro -e minim.edr

8. Two step equilibration

        #!bash
        echo "define        = -DPOSRES  ; position restrain the protein
        ; Run parameters
        integrator  = md        ; leap-frog integrator
        nsteps      = 50000     ; 2 * 50000 = 100 ps
        dt          = 0.002     ; 2 fs
        ; Output control
        nstxout     = 500       ; save coordinates every 1.0 ps
        nstvout     = 500       ; save velocities every 1.0 ps
        nstenergy   = 500       ; save energies every 1.0 ps
        nstlog      = 500       ; update log file every 1.0 ps
        ; Bond parameters
        continuation            = no        ; first dynamics run
        constraint_algorithm    = lincs     ; holonomic constraints 
        constraints             = all-bonds ; all bonds (even heavy atom-H bonds)
        constrained
        lincs_iter              = 1         ; accuracy of LINCS
        lincs_order             = 4         ; also related to accuracy
        ; Neighborsearching
        cutoff-scheme   = Verlet
        ns_type         = grid      ; search neighboring grid cells
        nstlist         = 10        ; 20 fs, largely irrelevant with Verlet
        rcoulomb        = 1.0       ; short-range electrostatic cutoff (in nm)
        rvdw            = 1.0       ; short-range van der Waals cutoff (in nm)
        ; Electrostatics
        coulombtype     = PME   ; Particle Mesh Ewald for long-range electrostatics
        pme_order       = 4     ; cubic interpolation
        fourierspacing  = 0.16  ; grid spacing for FFT
        ; Temperature coupling is on
        tcoupl      = V-rescale             ; modified Berendsen thermostat
        tc-grps     = Protein Non-Protein   ; two coupling groups - more accurate
        tau_t       = 0.1     0.1           ; time constant, in ps
        ref_t       = 300     300           ; reference temperature, one for each
        group, in K
        ; Pressure coupling is off
        pcoupl      = no        ; no pressure coupling in NVT
        ; Periodic boundary conditions
        pbc     = xyz           ; 3-D PBC
        ; Dispersion correction
        DispCorr    = EnerPres  ; account for cut-off vdW scheme
        ; Velocity generation
        gen_vel     = yes       ; assign velocities from Maxwell distribution
        gen_temp    = 300       ; temperature for Maxwell distribution
        gen_seed    = -1        ; generate a random seed" > nvt.mdp

        gmx grompp -f nvt.mdp -c minim.gro -p topol.top -o nvt.tpr

        gmx mdrun -s nvt.tpr -o nvt.trr -c nvt.gro -e nvt.edr -cpo nvt.cpt

        echo "define        = -DPOSRES  ; position restrain the protein
        ; Run parameters
        integrator  = md        ; leap-frog integrator
        nsteps      = 50000     ; 2 * 50000 = 100 ps
        dt          = 0.002     ; 2 fs
        ; Output control
        nstxout     = 500       ; save coordinates every 1.0 ps
        nstvout     = 500       ; save velocities every 1.0 ps
        nstenergy   = 500       ; save energies every 1.0 ps
        nstlog      = 500       ; update log file every 1.0 ps
        ; Bond parameters
        continuation            = yes       ; Restarting after NVT 
        constraint_algorithm    = lincs     ; holonomic constraints 
        constraints             = all-bonds ; all bonds (even heavy atom-H bonds)
        constrained
        lincs_iter              = 1         ; accuracy of LINCS
        lincs_order             = 4         ; also related to accuracy
        ; Neighborsearching
        cutoff-scheme   = Verlet
        ns_type         = grid      ; search neighboring grid cells
        nstlist         = 10        ; 20 fs, largely irrelevant with Verlet scheme
        rcoulomb        = 1.0       ; short-range electrostatic cutoff (in nm)
        rvdw            = 1.0       ; short-range van der Waals cutoff (in nm)
        ; Electrostatics
        coulombtype     = PME       ; Particle Mesh Ewald for long-range electrostatics
        pme_order       = 4         ; cubic interpolation
        fourierspacing  = 0.16      ; grid spacing for FFT
        ; Temperature coupling is on
        tcoupl      = V-rescale             ; modified Berendsen thermostat
        tc-grps     = Protein Non-Protein   ; two coupling groups - more accurate
        tau_t       = 0.1     0.1           ; time constant, in ps
        ref_t       = 300     300           ; reference temperature, one for each
        group, in K
        ; Pressure coupling is on
        pcoupl              = Parrinello-Rahman     ; Pressure coupling on in NPT
        pcoupltype          = isotropic             ; uniform scaling of box vectors
        tau_p               = 2.0                   ; time constant, in ps
        ref_p               = 1.0                   ; reference pressure, in bar
        compressibility     = 4.5e-5                ; isothermal compressibility of
        water, bar^-1
        refcoord_scaling    = com
        ; Periodic boundary conditions
        pbc     = xyz       ; 3-D PBC
        ; Dispersion correction
        DispCorr    = EnerPres  ; account for cut-off vdW scheme
        ; Velocity generation
        gen_vel     = no        ; Velocity generation is off" > npt.mdp

        gmx grompp -f npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -o npt.tpr

        gmx mdrun -s npt.tpr -o npt.trr -c npt.gro -e npt.edr -cpo npt.cpt

9. Run 1ns molecular dynamics

        #!bash
        echo "; Run parameters
        integrator  = md        ; leap-frog integrator
        nsteps      = 500000    ; 2 * 500000 = 1000 ps (1 ns)
        dt          = 0.002     ; 2 fs
        ; Output control
        nstxout             = 5000      ; save coordinates every 10.0 ps
        nstvout             = 5000      ; save velocities every 10.0 ps
        nstenergy           = 5000      ; save energies every 10.0 ps
        nstlog              = 5000      ; update log file every 10.0 ps
        nstxout-compressed  = 5000      ; save compressed coordinates every 10.0 ps
                                        ; nstxout-compressed replaces nstxtcout
        compressed-x-grps   = System    ; replaces xtc-grps
        ; Bond parameters
        continuation            = yes       ; Restarting after NPT 
        constraint_algorithm    = lincs     ; holonomic constraints 
        constraints             = all-bonds ; all bonds (even heavy atom-H bonds)
        constrained
        lincs_iter              = 1         ; accuracy of LINCS
        lincs_order             = 4         ; also related to accuracy
        ; Neighborsearching
        cutoff-scheme   = Verlet
        ns_type         = grid      ; search neighboring grid cells
        nstlist         = 10        ; 20 fs, largely irrelevant with Verlet scheme
        rcoulomb        = 1.0       ; short-range electrostatic cutoff (in nm)
        rvdw            = 1.0       ; short-range van der Waals cutoff (in nm)
        ; Electrostatics
        coulombtype     = PME       ; Particle Mesh Ewald for long-range electrostatics
        pme_order       = 4         ; cubic interpolation
        fourierspacing  = 0.16      ; grid spacing for FFT
        ; Temperature coupling is on
        tcoupl      = V-rescale             ; modified Berendsen thermostat
        tc-grps     = Protein Non-Protein   ; two coupling groups - more accurate
        tau_t       = 0.1     0.1           ; time constant, in ps
        ref_t       = 300     300           ; reference temperature, one for each
        group, in K
        ; Pressure coupling is on
        pcoupl              = Parrinello-Rahman     ; Pressure coupling on in NPT
        pcoupltype          = isotropic             ; uniform scaling of box vectors
        tau_p               = 2.0                   ; time constant, in ps
        ref_p               = 1.0                   ; reference pressure, in bar
        compressibility     = 4.5e-5                ; isothermal compressibility of
        water, bar^-1
        ; Periodic boundary conditions
        pbc     = xyz       ; 3-D PBC
        ; Dispersion correction
        DispCorr    = EnerPres  ; account for cut-off vdW scheme
        ; Velocity generation
        gen_vel     = no        ; Velocity generation is off" > md.mdp

        gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md1ns.tpr

        gmx mdrun -s md1ns.tpr -o md1ns.trr -c md1ns.gro -e md1ns.edr -cpo md1ns.cpt
