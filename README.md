[![Codacy Badge](https://api.codacy.com/project/badge/Grade/3f9ac104a1444a57a1a5287e95830a84)](https://www.codacy.com/app/andriopau/pymdsetup?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bioexcel/pymdsetup&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/pymdsetup/badge/?version=latest)](http://pymdsetup.readthedocs.io/en/latest/?badge=latest)

# Pymdsetup

### Introduction
Pymdsetup is a python package to setup systems to run molecular
dynamics simulations.
If you have already installed the package you should check our [latest API documentation](http://pymdsetup.readthedocs.io/en/latest/).

### Version 1.0
This version is just an example of a functional workflow.
In v0.2 Pymdsetup uses the following applications:

1. GROMACS: Open source and widely used molecular dynamics simulation package.
(http://www.gromacs.org/)
2. SCWRL4: Application to determine the protein side chain conformations.
(http://dunbrack.fccc.edu/scwrl4/)
3. GNUPLOT: Gnuplot is a portable command-line driven graphing utility for
Linux (http://www.gnuplot.info/)
4. PyCOMPSs (optional just for parallel executions): Python library for parallel computing.
(https://www.bsc.es/computer-sciences/grid-computing/comp-superscalar/programming-model/python)

### Online Installation

(We are assuming that you are installing Pymdsetup in your home directory `cd ~`)

1. Install CMAKE, GNUPLOT and PIP:

    ```bash
    sudo apt-get -y install git vim htop cmake gnuplot python-pip
    ```

2. Install numpy biopython pyyaml requests and nose Python libraries:

    ```bash
    sudo pip install --upgrade pip
    sudo pip install numpy biopython pyyaml requests nose
    ```
3. Clone the project and add the project path to the PYTHONPATH variable:

    ```bash
    git clone https://github.com/bioexcel/pymdsetup.git
    export PYTHONPATH=~/pymdsetup:$PYTHONPATH
    #If you want to make this change permanent in your .bashrc file:
    echo "export PYTHONPATH=~/pymdsetup:\$PYTHONPATH" >> ~/.bashrc
    ```
4. Register in http://dunbrack.fccc.edu/scwrl4/license/index.html, download
the "install_Scwrl4_Linux" executable file, run the following commands:

    ```bash
    chmod u+x install_Scwrl4_Linux
    ./install_Scwrl4_Linux
    ```
And follow the SCWRL4 interactive installation instructions.

5. Download and install GROMACS 5.1:

    ```bash
    wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-5.1.2.tar.gz
    # From the 5.1.2 Gromacs install guide
    # http://manual.gromacs.org/documentation/5.1.2/install-guide/index.html
    tar xfz gromacs-5.1.2.tar.gz
    cd gromacs-5.1.2
    mkdir build
    cd build
    cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON
    make
    make check
    sudo make install
    source /usr/local/gromacs/bin/GMXRC
    #If you want to make this change permanent in your .bashrc file:
    echo "source /usr/local/gromacs/bin/GMXRC" >> ~/.bashrc
    ```

### No Internet connection installation using Anaconda
https://www.anaconda.com/  
(Assuming that you already installed GROMACS, SCWRL4 and GNUPLOT)

1. On your local connected computer, download Pymdsetup, Anaconda and the Biopython Anaconda package and copy them to the offline computer:

    ```bash
    sudo apt-get install -y git
    git clone https://github.com/bioexcel/pymdsetup.git
    wget https://repo.continuum.io/archive/Anaconda2-5.1.0-Linux-x86_64.sh
    wget https://repo.continuum.io/pkgs/free/linux-64/biopython-1.69-np113py27_0.tar.bz2

    ```
*Copy all files to the disconnected computer*

2. On the disconnected computer:

    ```bash
    bash Anaconda2-5.1.0-Linux-x86_64.sh
    source .bashrc
    mv biopython-1.69-np113py27_0.tar.bz2 anaconda2/pkgs/
    conda install anaconda2/pkgs/biopython-1.69-np113py27_0.tar.bz2
    conda install --use-index-cache --offline --use-local  numpy pyyaml requests nose
    echo "~/pymdsetup" > ~/anaconda2/lib/python2.7/site-packages/pymdsetup.pth
    ```

### Using Pymdsetup

### Copyright & Licensing
This software has been developed in the MMB group (http://mmb.pcb.ub.es) at the
BSC (http://www.bsc.es/) & IRB (https://www.irbbarcelona.org/) for the European BioExcel (http://bioexcel.eu/), funded by the European Commission
(EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2017 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2017 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file
[LICENSE](LICENSE) for details.

<!--
The file [NOTICE](NOTICE) contains any additional attributions and
details about embedded third-party libraries and source code.
-->


![](docs/source/_static/bioexcel_logo.png "Bioexcel")
