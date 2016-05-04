# Debug
runcompss -d --lang=python --classpath=/home/compss/PyCOMPSs/git/pymdsetup/:/pymdsetup/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/PyCOMPSs/git/pymdsetup/workflows/gromacs_full_pycompss.py
# Graph
runcompss -g --lang=python --classpath=/home/compss/PyCOMPSs/git/pymdsetup/:/pymdsetup/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/PyCOMPSs/git/pymdsetup/workflows/gromacs_full_pycompss.py
# Tracing
runcompss --tracing=True --lang=python --classpath=/home/compss/PyCOMPSs/git/pymdsetup/:/pymdsetup/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/PyCOMPSs/git/pymdsetup/workflows/gromacs_full_pycompss.py
