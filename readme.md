# pymdsetup

### Introduction
Pymdsetup is a python module to setup systems to run a molecular
dynamics simulation.

### Installation
1. Download & Install Anaconda5

    ```bash
    wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda2-2.5.0-Linux-x86_64.sh
    bash Anaconda2-2.5.0-Linux-x86_64.sh
    ```

2. Create an Anaconda environment

    ```bash
    conda create --name
    ```

### GROMACS installation
1. Download Gromacs package v.5.1.2 (February 2016)

    
    ```#!bash
    wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-5.1.2.tar.gz
    mv gromacs-5.1.2.tar.gz $HOME/soft/gromacs/
    cd $HOME/soft/gromacs/
    ```

    

2. Extract package

    ```bash
    tar xzvf gromacs-5.1.2.tar.gz
    rm -rf gromacs-5.1.2.tar.gz
    cd gromacs-5.1.2/
    ```

3. Build from source

    ```bash
    mkdir build
    cd build/
    cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON
    make
    make check
    sudo make install
    source /usr/local/gromacs/bin/GMXRC
    ```

### GROMACS not automated setup tutorial
(source: http://www.gromacs.org/@api/deki/files/198/=gmx-tutorial.pdf)
1.