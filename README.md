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


TODO: Change this tutorial to adapt it to GROMACS 5.x.x

1. Download the Lysozyme PDB structure

        #!bash
        curl mmb.irbbarcelona.org/api/pdb/1lyd/entry > 1lyd.pdb

2. Creating Gromacs topology from the PDB file

        #!bash
        gmx pdb2gmx -f 1lyd.pdb -water tip3p -ff amber99sb-ildn

3. Creating the water box

        #!bash
        gmx editconf -f conf.gro -bt dodecahedron -d 0.5 -o box.gro
        gmx solvate -cp box.gro -cs spc216.gro -o 1AKI_solv.gro -p topol.top

4. Running an energy minimization

        #!bash
        echo "integrator      = steep
        nsteps          = 200
        nstlist         = 10
        cutoff-scheme   = verlet
        vdw-type        = cut-off
        rvdw            = 1.0
        coulombtype     = pme
        rcoulomb        = 1.0" > em.mdp
        
