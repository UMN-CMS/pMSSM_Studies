import os, argparse, glob, tarfile
from os import system, environ

def importlib(module, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(module, path)
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)

    return lib

# Pass in a list of files to tar up along with a location
# to tar them up at
def makeExeAndFriendsTarrball(filestoTransfer, path, tag):
    system("mkdir -p %sstuff"%(tag))
    for fn in filestoTransfer:
        system("cd %sstuff; ln -s %s" %(tag,fn))
    
    tarallinputs = "tar czvf %s/%sstuff.tar.gz %sstuff --dereference"%(path, tag, tag)
    system(tarallinputs)
    system("rm -r %sstuff"%(tag))

if __name__ == '__main__':

    RecursiveFileList = importlib("RecursiveFileList", "/cvmfs/cms-lpc.opensciencegrid.org/FNALLPC/lpc-scripts/RecursiveFileList.py")

    parser = argparse.ArgumentParser()
    parser.add_argument("--noSubmit"   , dest="noSubmit"   , help="do not submit to cluster"   , default=False, action="store_true")
    parser.add_argument("--inputDir"   , dest="inputDir"   , help="Input dir to SLHA"          , type=str     , default="")
    parser.add_argument("--outputDir"  , dest="outputDir"  , help="Output dir to write output" , type=str     , default=".")
    parser.add_argument("--filesPerJob", dest="filesPerJob", help="Files per job"              , type=int     , default=1)
    
    args = parser.parse_args()
    
    inputDir    = args.inputDir
    outputDir   = args.outputDir
    filesPerJob = args.filesPerJob
    
    pythia    = "pythia8305"
    delphes   = "Delphes-3.5.0"

    USER = os.environ["USER"]
    
    installPath = "/uscms/home/%s/nobackup/pmssm/"%(USER)
    eosPath     = "/eos/uscms/store/user/%s/"%(USER)
    
    inputStub = ""
    if "*" in inputDir:
        inputStub = "/".join(inputDir.split("/")[0:-1])
    else:
        inputStub = inputDir
    
    pythiaPath  = "%s/%s/"%(installPath,pythia)
    delphesPath = "%s/%s/"%(installPath,delphes)
    
    # Here is the configuration for the Data/MC validation of the TopTagger 
    pythiaFilestoTransfer  = [
                                 installPath + "run.py", 
                                 pythiaPath  + "examples/pmssm"
                             ]
    
    # make directory for condor submission
    if not os.path.isdir("%s/output-files" % (outputDir)):
        os.makedirs("%s/output-files" % (outputDir))
    
    if not os.path.isdir("%s/log-files" % (outputDir)):
        os.makedirs("%s/log-files" % (outputDir))
    
    if not os.path.isdir("%s/%s"%(eosPath, outputDir)):
        os.makedirs("%s/%s/"%(eosPath, outputDir))
    
    # Tar up everything we need including pythia and Delphes
    makeExeAndFriendsTarrball(pythiaFilestoTransfer, outputDir, "pythia")
    system("tar --exclude-caches-all --exclude-vcs -zcf %s/%s.tar.gz -C %s bin lib share/Pythia8/"%(outputDir, pythia, pythia))
    system("tar --exclude-caches-all --exclude-vcs -zcf %s/%s.tar.gz -C %s cards modules DelphesHepMC3 DelphesEnv.sh $(cd %s; echo *.pcm)"%(outputDir, delphes, delphes, delphes))
    
    # Write out condor submit file
    fout = open("condor_submit.txt", "w")
    fout.write("universe              = vanilla\n")
    fout.write("Executable            = run.sh\n")
    fout.write("Requirements          = OpSys == \"LINUX\" && (Arch != \"DUMMY\")\n")
    fout.write("Should_Transfer_Files = YES\n")
    fout.write("Request_Memory        = 5120M\n")
    fout.write("WhenToTransferOutput  = ON_EXIT\n")
    fout.write("Transfer_Input_Files  = %s/%s/pythiastuff.tar.gz, %s/%s/%s.tar.gz, %s/%s/%s.tar.gz\n" %(environ["PWD"], outputDir, environ["PWD"], outputDir, pythia, environ["PWD"], outputDir, delphes))
    fout.write("x509userproxy         = $ENV(X509_USER_PROXY)\n\n")
    
    inputs = RecursiveFileList.get_file_list(inputDir)
    inputs = [p for p in inputs if ".tar.gz" in p]

    majorCounter = 0
    for iPath in range(0, len(inputs)):

        path = inputs[iPath]

        ftar = tarfile.open(path)
        members = ftar.getmembers()
        members = [m for m in members if ".slha" in m.name]

        minorCounter = 1
        lastMember = False
        for iMember in range(0, len(members)):

            member = members[iMember]

            if iMember == len(members)-1: lastMember = True
        
            tag = member.name.rpartition("/")[0].replace("/", "_")

            outName = "output_fcc_%d"%(majorCounter)

            if minorCounter == 1:
                fout.write("Arguments = %s %s %s %s %s"%(outName, pythia, delphes, path, outputDir))

            fout.write(" %s"%(member.name))
            minorCounter += 1

            if minorCounter > filesPerJob or lastMember:

                fout.write("\n")
                fout.write("transfer_output_remaps = \"%s.txt = %s/output-files/%s.txt\"\n"%(outName, outputDir, outName))
                fout.write("Output    = %s/log-files/%s.stdout\n"%(outputDir, outName))
                fout.write("Error     = %s/log-files/%s.stderr\n"%(outputDir, outName))
                fout.write("Log       = %s/log-files/%s.log\n"%(outputDir, outName))
                fout.write("Queue\n\n")

                minorCounter  = 1
                majorCounter += 1

            #break
        #break

        ftar.close()
    fout.close()
    
    if not args.noSubmit: 
        system('mkdir -p logs')
        system("echo 'condor_submit condor_submit.txt'")
        system('condor_submit condor_submit.txt')
    
    print("Submission directory: %s"%(args.outputDir))
