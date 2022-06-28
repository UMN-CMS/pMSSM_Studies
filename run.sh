#! /bin/bash

TAG=$1       # Tag to keep track of things
shift
PYTHIA=$1    # Name of pythia install folder
shift
DELPHES=$1   # Name of Delphes install folder
shift
TARPATH=$1   # Tar containing SLHA files
shift
OUTPUTDIR=$1 # Which folder in user EOS to put ROOT files
shift
SLHAPATHS=$@  # Path to SLHA file inside tar

TARFILE=${TARPATH##*/}

# Get the correct ROOT and GCC for running things
source /cvmfs/sft.cern.ch/lcg/views/LCG_99/x86_64-centos7-gcc10-opt/setup.sh

# Override PYTHIA/DELPHES environment vars with local version of pythia/delphes
export PYTHIA8=`pwd`/${PYTHIA}
export PYTHIA8DATA=`pwd`/${PYTHIA}/share/Pythia8/xmldoc

mkdir -p ${PYTHIA}/test
mv ${PYTHIA}.tar.gz pythiastuff.tar.gz ${PYTHIA}

mkdir -p ${DELPHES}
mv ${DELPHES}.tar.gz ${DELPHES}

cd ${PYTHIA}

tar -xzf ${PYTHIA}.tar.gz
tar -xzf pythiastuff.tar.gz

mv pythiastuff/* test

cd test

mkdir inputs

OLDDIR="/eos/uscms/"
NEWDIR="root://cmseos.fnal.gov///"
NEWTARPATH=${TARPATH/$OLDDIR/$NEWDIR}

xrdcp -r ${NEWTARPATH} inputs

for SLHAPATH in ${SLHAPATHS}
do
    SLHAFILE=${SLHAPATH##*/}
    SLHA=${SLHAPATH%%.*}
    NEWNAME=${SLHA//\//__}

    tar -xzf inputs/${TARFILE} -C inputs ${SLHAPATH} --strip=1
    mv inputs/${SLHAFILE} inputs/${NEWNAME}.slha
done

for SLHA in inputs/*.slha
do
    SLHANAME=${SLHA%%.*}
    SLHANAME=${SLHANAME##*/}

    python run.py --slha ${SLHA} --tag ${TAG}

    mv myMSSM.HepMC ../../${DELPHES}/${SLHANAME}.HepMC
done

mv output_*.txt ${_CONDOR_SCRATCH_DIR}

cd ../../${DELPHES}

tar -xzf ${DELPHES}.tar.gz

source DelphesEnv.sh

export DELPHES_DIR=`pwd`/${DELPHES}
export DELPHES_HOME=`pwd`/${DELPHES}

echo $DELPHES_HOME
echo $PYTHONPATH
echo $LD_LIBRARY_PATH
echo $LIBRARY_PATH

ls -lrth

for HEPMC in *.HepMC
do
    OUTNAME=${HEPMC%%.*}
    echo $OUTNAME

    ./DelphesHepMC3 ./cards/FCC/FCChh.tcl ${OUTNAME}.root ${OUTNAME}.HepMC
done

for ROOT in *.root
do
    xrdcp ${ROOT} root://cmseos.fnal.gov//store/user/`whoami`/${OUTPUTDIR}/${ROOT}
done

rm *.root
