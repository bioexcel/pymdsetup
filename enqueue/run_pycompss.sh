#!/bin/bash
runcompss -d -g -m --lang=python --pythonpath=/home/compss/pymdsetup/:/home/compss/ /home/compss/pymdsetup/workflows/gromacs_full_pycompss.py /home/compss/pymdsetup/workflows/conf_2mut_nt0.yaml virtualbox 
# sudo killall gmx
# sudo killall java
# /etc/init.d/compss-monitor start &
# runcompss -d -g -m --lang=python --pythonpath=/home/compss/pymdsetup/:/home/compss/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/pymdsetup/workflows/gromacs_full_pycompss.py &
# firefox http://localhost:8080/compss-monitor &
