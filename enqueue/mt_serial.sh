#!/bin/bash
#SBATCH --job-name=k80_serial
#SBATCH --partition=projects
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH -o k80_serial_%j.out
#SBATCH -e k80_serial_%j.err
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=4
#SBATCH --constraint=k80
#SBATCH --gres gpu:4
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

module purge
module load K80 intel/15.0.0 impi/5.1.3.181 cuda/7.5 mkl/11.2 GROMACS/5.1.2
python /home/bsc23/bsc23210/pymdsetup/workflows/gromacs_full.py /home/bsc23/bsc23210/pymdsetup/workflows/conf_2mut_gpu.yaml minotauro 1

# mnsubmit mt_serial.sh
