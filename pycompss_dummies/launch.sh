# Debug Graph
sudo killall java; runcompss -d -g --lang=python --classpath=/home/compss/pymdsetup/:/pymdsetup/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/pymdsetup/workflows/gromacs_full_pycompss.py

# Tracing
sudo killall java; runcompss --tracing=True --lang=python --classpath=/home/compss/pymdsetup/:/pymdsetup/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/pymdsetup/workflows/gromacs_full_pycompss.py
