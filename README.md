For setting up a PYTHIA+Delphes pipeline to process SLHA files and simulate SUSY events in a collider

## Setting up the Working Area

Initial setup of the working area is done by running `setup_pmssm.sh`.
This shell script downloads and compiles Delphes, Pythia, and HepMC.
The current version of these three packages (specified in the setup script) are known to be compatible with one another.

Provided in this repository is a small source file `pmssm.cc` to be compiled and used to run Pythia.
Running the setup script places this file in the `examples` directory of the Pythia folder and the `MakeFile` is edited to allow compilation of `pmssm.cc`.

## Submitting Jobs to Condor

The intent of this code is to be cluster-submission-focused and has some nuances for running on the Condor cluster at LPC.
However, this setup and workflow should be easily adaptable to the UMN-CMS Condor cluster with minimal changes

An example call to the main submission script (`submit.py`), which utilizes all the options would be:
```
python submit.py --noSubmit --outputDir ProdV4 --inputDir /eos/uscms/store/user/jennetd/snowmass/spheno-4.05/test_lin_0.05/ --filesPerJob 2
```

The specified output directory is made in the current working directory and stores logs and text files from the jobs.
The number of SLHA files to process in a job is specified via the last argument.
The input directory is a path (here assumed to be on EOS and accessible at LPC) that contains SLHA files.
N.B. the code is set up to specifically process tar-ed SLHA files as made by LPC user `jennetd` (J. Dickinson).

The jobs execute the `run.sh` shell script, which ultimately executes `run.py`i.
Via `run.py`, Pythia is run while loading in one of the SLHA files extracted from tar.
Around 10000 events are generated with all SUSY processes turned on

Once Pythia has finished and generated a HepMC file, this file is loaded into Delphes where the events can be simulated in a collider detector.
The final output(s) returned to the user are a ROOT file containing the simulated events and placed in their EOS area with the same output folder name as well as a text file with some scraped information from Pythia regarding cross sections for different processes.
