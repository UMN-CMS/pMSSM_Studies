This repository is for setting up a little framework that loads SLHA files into Pythia to generate SUSY particle production in a collider.
The output from Pythia is passed to Delphes, which simulates these SUSY particles and their decays in an actual collider detector.
Final output are ROOT files with the simulated events in simple TTree structure for processing.

## Setting up the Working Area

Initial setup of the working area is done by simply running `setup_pmssm.sh`.
This shell script downloads and compiles Delphes, Pythia, and HepMC.
The current version of these three packages (as specified in the setup script at the time of this writing) are known to be compatible with one another.

Also provided in this repository is a small source file `pmssm.cc` to be compiled for and used to run Pythia.
Running the setup script places this file in the `examples` directory of the Pythia folder and the `MakeFile` is automatically edited to allow compilation of `pmssm.cc`.

## Submitting Jobs to Condor

The intent of this code base is to be cluster-submission-focused and has some nuances for running on the Condor cluster at the LPC.
However, this setup and workflow should be easily adaptable to the UMN-CMS Condor cluster with minimal changes.

An example call to the main submission script (`submit.py`), which utilizes all the options would be:
```
python submit.py --noSubmit --outputDir ProdV4 --inputDir /eos/uscms/store/user/jennetd/snowmass/spheno-4.05/test_lin_0.05/ --filesPerJob 2
```

The specified output directory is made in the current working directory and stores logs and text files from the jobs.
The number of SLHA files to process in a job is specified via the last argument.
The input directory is a path (here assumed to be on EOS and accessible at the LPC) that contains SLHA files.
N.B. the code is set up to specifically process tar-ed SLHA files as made by LPC user `jennetd` (J. Dickinson).

The jobs execute the `run.sh` shell script, which ultimately executes `run.py`.
Via `run.py`, Pythia is run while loading in the SLHA files extracted from tar, one-at-a-time.
Around 10000 events (specified in `run.py`) are generated with all SUSY processes turned on.
The script also generates a `.cmnd` file on-the-fly for configuring Pythia to generate events as specified.

Once Pythia has finished and generated a HepMC file, this file is loaded into Delphes where the events can be simulated in a collider detector.
Within `run.sh`, the user can specify which detector "card" to load into Delphes for simulation.
The final output(s) returned to the user are two-fold.
There is a ROOT file(s) containing the simulated events and placed in the user's EOS area with the same output folder name as specified above.
Likewise, there is a text file(s) with some scraped information from Pythia regarding cross sections for different processes.
