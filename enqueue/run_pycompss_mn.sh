#!/bin/bash

enqueue_compss \
  --job_dependency=$1 \
  --exec_time=$2 \
  --num_nodes=$3 \
  --qos=$4 \
  --network=infiniband \
  --lang=python \
  --pythonpath=/gpfs/home/bsc23/bsc23210/pymdsetup/:/gpfs/home/bsc23/bsc23210/ \
  --master_working_dir=/gpfs/scratch/bsc23/bsc23210/ \
  --worker_working_dir=/gpfs/scratch/bsc23/bsc23210/ \
  --tracing=$5 \
  --graph=$6 \
  --log_level=debug \
  --base_log_dir=/gpfs/scratch/bsc23/bsc23210/ \
  --worker_in_master_cpus=0 \
  --jvm_workers_opts=\"-Dcompss.worker.removeWD=false\" \
/gpfs/home/bsc23/bsc23210/pymdsetup/workflows/pyruvateKinase_MN.py ${7} ${8} ${9} ${10} ${11} ${12} ${13} ${14} ${15} ${16} ${17} ${18} ${19} ${20}


#  --master_port=46000 \
#  --qos=debug \
#  --qos=xprace \
#  --max_tasks_per_node=1 \
#  --worker_working_dir=scratch \
#  --jvm_workers_opts=\"-Dcompss.worker.removeWD=false\" \

#Example:

#bash /gpfs/home/bsc23/bsc23210/pymdsetup/enqueue/run_pycompss_mn.sh None 15 3 xprace false false /gpfs/home/bsc23/bsc23210/pymdsetup/workflows/conf/conf_pyruvateKinase_MN_test.yaml mare_nostrum 0 2

#Explanation:

#interpreter              -> bash
#enqueue compss script    -> run_pycompss_mn.sh (This script)
#$1 job_dependency        -> None (Or job name/number to wait for)
#$2 exec_time             -> 15 (Wall time in minutes)
#$3 num_nodes	          -> 3 (Number of MN nodes)
#$4 qos                   -> debug (Queue)
#$5 tracing               -> false (create pycompss execution traces)
#$6 graph                 -> false (create pycompss graph)
#$7 yaml config file      -> /gpfs/home/bsc23/bsc23210/pymdsetup/workflows/conf/conf_pyruvateKinase_MN_test.yaml (this is the test one)
#$8 system                -> mare_nostrum (key for system paths in the config yaml file)
#$9 mut_start             -> 0 (start mutation)
#$10 mut_end              -> 2 (end mutation)
