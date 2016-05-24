# Debug Graph
sudo killall java; runcompss -d -g --lang=python --classpath=/home/compss/pymdsetup/:/pymdsetup/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/pymdsetup/workflows/gromacs_full_pycompss.py

# Tracing
sudo killall java; runcompss --tracing=True --lang=python --classpath=/home/compss/pymdsetup/:/pymdsetup/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/pymdsetup/workflows/gromacs_full_pycompss.py

# /usr/local/gromacs/bin/gmx grompp -f /home/compss/pymdsetup/testworkflow/A.VAL2GLY/step7_gppions/gmx_full_ions.mdp -c /home/compss/pymdsetup/testworkflow/A.VAL2GLY/step6_sol/sol.gro -p /home/compss/pymdsetup/testworkflow/A.VAL2GLY/step6_sol/sol.top -o /home/compss/pymdsetup/testworkflow/A.VAL2GLY/step7_gppions/gppions.tpr
# /usr/local/gromacs/bin/gmx grompp -f /home/compss/pymdsetup/testworkflow/A.VAL2GLY/step7_gppions/gmx_full_ions.mdp -c /home/compss/pymdsetup/testworkflow/A.VAL2GLY/step6_sol/sol.gro -p /home/compss/pymdsetup/testworkflow/A.VAL2GLY/step6_sol/sol.top -o /home/compss/pymdsetup/testworkflow/A.VAL2GLY/step7_gppions/gppions.tpr
