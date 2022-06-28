#! /bin/bash

LOCALAREA=`pwd`

DELPHES="Delphes-3.5.0"
HEPMC="HepMC3-3.2.2"
PYTHIA="pythia8306"

# Source for ROOT and GCC
source /cvmfs/sft.cern.ch/lcg/views/LCG_99/x86_64-centos7-gcc10-opt/setup.sh

cd ${LOCALAREA}

# Get Delphes and make it
wget http://cp3.irmp.ucl.ac.be/downloads/Delphes-3.5.0.tar.gz
tar -zxf ${DELPHES}.tar.gz

cd ${DELPHES}
make -j 4

cd ${LOCALAREA}

# Get HepMC3 and build it and install it
wget http://hepmc.web.cern.ch/hepmc/releases/${HEPMC}.tar.gz
tar -xzf ${HEPMC}.tar.gz

mkdir HepMC3 HepMC3-build
cd HepMC3-build 

cmake -DHEPMC3_ENABLE_ROOTIO:BOOL=OFF -DHEPMC3_ENABLE_TEST:BOOL=OFF  -DHEPMC3_INSTALL_INTERFACES:BOOL=ON -DHEPMC3_ENABLE_PYTHON:BOOL=ON -DHEPMC3_PYTHON_VERSIONS=2.7 -DHEPMC3_BUILD_STATIC_LIBS:BOOL=OFF -DHEPMC3_BUILD_DOCS:BOOL=OFF  -DCMAKE_INSTALL_PREFIX=../HepMC3   -DHEPMC3_Python_SITEARCH27=../Hep3MC/lib/python2.7/site-packages ${LOCALAREA}/${HEPMC}

make -j 4
make install

cd ${LOCALAREA}

# Get pythia and make it
wget https://pythia.org/download/pythia83/${PYTHIA}.tgz
tar xvfz ${PYTHIA}.tgz

cd ${PYTHIA}

./configure --with-hepmc3-config=${LOCALAREA}/HepMC3/bin/HepMC3-config --with-hepmc3-bin=${LOCALAREA}/HepMC3/bin --with-hepmc3-lib=${LOCALAREA}/HepMC3/lib64 --with-hepmc3-include=${LOCALAREA}/HepMC3/include

cp ../pmssm.cc examples/

sed -i 's/main41/pmssm main41/g' examples/MakeFile

make -j 4

cd ${LOCALAREA}

rm *.tar.gz *.tgz
