#! /bin/env python

import subprocess, os, argparse, math

def makeXsecUncStr(xsec, xsecUnc):

    xsecMag    = math.floor(math.log(xsec, 10))
    xsecMagUnc = math.floor(math.log(xsecUnc, 10))

    magDiff = xsecMag - xsecMagUnc

    bdec = abs(xsecMag) + 1
    adec = 3 - abs(xsecMag)
    if xsecMag < -4:
        bdec = 1
        adec = 3
    elif xsecMag < 0:
        bdec = 0
        adec = 4
    elif xsecMag >= 4:
        adec = 0

    newXSecStr = ""; newXSecUncStr = ""
    if xsecMag < -4:
        newXSecStr = "{:{}.{}g}".format(xsec, bdec, adec)
        newXSecUncStr = "{:{}.{}g}".format(xsecUnc, bdec, adec)
    else:
        newXSecStr = "{:{}.{}f}".format(xsec, bdec, adec)
        newXSecUncStr = "{:{}.{}f}".format(xsecUnc, bdec, adec)

    return "%s +/- %s"%(newXSecStr, newXSecUncStr)

def makeXsecStr(xsec):
    xsecMag    = math.floor(math.log(xsec, 10))

    bdec = abs(xsecMag) + 1
    adec = 3 - abs(xsecMag)
    if xsecMag < -4:
        bdec = 1
        adec = 3
    elif xsecMag < 0:
        bdec = 0
        adec = 4
    elif xsecMag >= 4:
        adec = 0

    newXSecStr = ""
    if xsecMag < -4:
        newXSecStr = "{:{}.{}g}".format(xsec, bdec, adec)
    else:
        newXSecStr = "{:{}.{}f}".format(xsec, bdec, adec)

    return newXSecStr

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--slha"     , dest="slha"     , help="SLHA file to process"       , type=str, default="")
    parser.add_argument("--outputDir", dest="outputDir", help="Output dir to write output" , type=str, default=".")
    parser.add_argument("--tag"      , dest="tag"      , help="Tag for output file"        , type=str, default="TEST")

    args = parser.parse_args()

    tag       = args.tag
    slha      = args.slha
    outputDir = args.outputDir

    #energies = [125, 3000, 30000, 10000]
    #intLumis = [20,  1000, 10000, 10000]

    energies = [100000]
    intLumis = [30000]

    cmnd = """! 1) Settings used in the main program.
            Main:numberOfEvents = 5000         ! number of events to generate
            Main:timesAllowErrors = 3          ! how many aborts before run stops\n
            ! 2) Settings related to output in init(), next() and stat().
            Init:showChangedSettings = off     ! list changed settings
            Init:showChangedParticleData = off ! list changed particle data
            Next:numberCount = 500             ! print message every n events
            Next:numberShowInfo = 0            ! print event information n times
            Next:numberShowProcess = 0         ! print process record n times
            Next:numberShowEvent = 0           ! print event record n times\n
            ! 3) Beam parameter settings. Values below agree with default ones.
            Beams:idA = 2212                 ! first beam, p = 2212, pbar = -2212
            Beams:idB = 2212                 ! second beam, p = 2212, pbar = -2212
            Beams:eCM = ENERGY              ! CM energy of collision\n
            ! 4) Read SLHA spectrum (a few examples are provided by default)
            SLHA:file = FILE               ! Sample SLHA2 spectrum
            SLHA:verbose = 0                    ! Print all SLHA information\n
            ! 5) Process selection
            SUSY:all = on                      ! Switches on ALL (~400) SUSY processes\n
            ! 6) Settings for the event generation process in the Pythia8 library.
            PartonLevel:MPI = on              ! multiparton interactions
            PartonLevel:ISR = on              ! initial-state radiation
            PartonLevel:FSR = on              ! final-state radiation
            HadronLevel:Hadronize = on        ! hadronization\n"""

    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    outname = tag
    outfile = open("%s.txt"%(outname), "a")

    processDicts = []
    started = os.stat("%s.txt"%(outname)).st_size != 0 
    beginScenario = True
    for iScenario in range(0, len(energies)):

        energy = energies[iScenario]
        intLumi = intLumis[iScenario]

        if not started:
            #outfile.write("Scenario 1: sqrt(s) = 125   GeV, int lumi 20    fb^-1\n")
            #outfile.write("Scenario 2: sqrt(s) = 3000  GeV, int lumi 1000  fb^-1\n")
            #outfile.write("Scenario 3: sqrt(s) = 30000 GeV, int lumi 10000 fb^-1\n")
            #outfile.write("Scenario 4: sqrt(s) = 10000 GeV, int lumi 10000 fb^-1\n\n")
        
            outfile.write("Scenario 1: sqrt(s) = 100000 GeV, int lumi 30000 fb^-1\n\n")

            temp = "S%d xsec [fb] (events)"
            #outfile.write("%s%s%s%s%s\n"%("SHLA".ljust(75), (temp%(1)).rjust(34), (temp%(2)).rjust(34), (temp%(3)).rjust(34), (temp%(4)).rjust(34) ) )

            outfile.write("%s%s\n"%("SHLA".ljust(75), (temp%(1)).rjust(34)))

            started = True

        if beginScenario:
            outfile.write("%s"%(("%s/%s;"%(tag, (slha.split("/")[-1]))).ljust(75)))
            beginScenario = False

        newCmnd = cmnd.replace("FILE", slha).replace("ENERGY", str(energy))
        cmndFile = open("pmssm.cmnd", "w")
        cmndFile.write(newCmnd)
        cmndFile.close()
    
        proc = subprocess.Popen(["./pmssm"], stdout=subprocess.PIPE)
        pythiaOutput = proc.stdout.readlines()
        lines = [line.decode("utf8").strip() for line in pythiaOutput]
    
        processDict = {}
        foundXsec = False
        xsec = -1.0; xsecUnc = -1.0; nEvents = 0.0
        for line in lines:

            if "PYTHIA Event and Cross Section Statistics" in line:
                foundXsec = True
                continue

            # Found a subprocess cross section line
            if "->" in line and foundXsec:
                chunks = line.split("| ")
                process = chunks[1].split("  ")[0]
                xsec    = float(chunks[-1].split("  ")[1].lstrip()) * 1e12

                if xsec != 0.0:
                    processDict[xsec] = process

            if "sum " in line and foundXsec:
                chunks = line.split("|")[-2].split("  ")
    
                # Convert to fb
                xsec    = float(chunks[1].lstrip()) * 1e12
                xsecUnc = float(chunks[2].rstrip()) * 1e12
                nEvents = xsec * intLumi
                break
    
        if xsec != -1.0:
            outfile.write(("%s (%.1f);"%(makeXsecUncStr(xsec, xsecUnc), nEvents)).rjust(34))
            #outfile.write("%s"%(("%.2e +/- %.2e (%.1f);"%(xsec, xsecUnc, nEvents)).rjust(34)))
        else:
            outfile.write("N/A;".rjust(34))

        processDicts.append(processDict)
    
    procStr = ""; procXsecStr = ""
    for processDict in processDicts:
        sortedKeys = list(sorted(processDict.keys(), reverse=True))
        for procXsec in sortedKeys:
            extra = ""
            if sortedKeys[-1] != procXsec: extra = ","
            procStr     += " %s"%(processDict[procXsec] + extra)
            procXsecStr += " %s"%(makeXsecStr(procXsec) + extra)

        procStr += ";"
        procXsecStr += ";"

    outfile.write(procStr)
    outfile.write(procXsecStr[:-1])
   
    outfile.write("\n")
    outfile.close()
