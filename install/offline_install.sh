#LOCAL
wget https://repo.continuum.io/archive/Anaconda2-5.0.0-Linux-x86_64.sh
wget https://repo.continuum.io/pkgs/free/linux-64/biopython-1.69-np113py27_0.tar.bz2
scp Anaconda2-5.0.0-Linux-x86_64.sh mn:~
#MN4
echo "module unload PYTHON" >> ~/.bashrc
echo "export testsys=mare_nostrum" >> ~/.bashrc
bash Anaconda2-5.0.0-Linux-x86_64.sh
source ~/.bashrc
#LOCAL
scp /home/pau/Downloads/biopython-1.69-np113py27_0.tar.bz2 mn:/home/bsc23/bsc23210/anaconda2/pkgs/
#MN4
conda install /home/bsc23/bsc23210/anaconda2/pkgs/biopython-1.69-np113py27_0.tar.bz2
conda install --use-index-cache --offline --use-local  numpy pyyaml requests nose
echo "/home/bsc23/bsc23210/pymdsetup" > /home/bsc23/bsc23210/anaconda2/lib/python2.7/site-packages/pymdsetup.pth
#REMEMBER: Change /home/bsc23/bsc23210/pymdsetup/scwrl4/Scwrl4.ini
