#!/bin/bash

export PYTHONPATH=/homea/ias-5/andrio/pymdsetup:$PYTHONPATH
/homea/ias-5/andrio/anaconda2/bin/python2.7 workflows/gromacs_full.py workflows/conf/conf_2mut_nt0_1ps.yaml jureca 1
