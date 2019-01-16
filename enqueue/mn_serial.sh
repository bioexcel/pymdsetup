#!/bin/bash
#BATCH -J pymdsetup_mpirun 
#SBATCH -o pymdsetup_mpirun.out
#SBATCH -e pymdsetup_mpirun.err
#SBATCH -D .
#SBATCH --ntasks=96
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=48
#SBATCH --nodes=2
#SBATCH -t 06:00:00
#SBATCH --qos=bsc_ls

module load gromacs/2016.4
python /home/bsc23/bsc23210/pymdsetup/workflows/pyruvateKinase.py /home/bsc23/bsc23210/pymdsetup/workflows/conf/conf_pyruvateKinase_MN_test.yaml mare_nostrum 2
