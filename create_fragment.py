import os,sys

StartFromLHE=False

MGLU = 500
GRIDPACK="<PATH TO GRIDPACK>"

FRAGMENT=""

if len(sys.argv)==1:
    print("Missing argument!!!")
    exit()
if len(sys.argv)>1:
    FRAGMENT="{}-Run3LHEGS-fragment.py".format(sys.argv[1])
if len(sys.argv)>2:
    MGLU=sys.argv[2]
if len(sys.argv)>3:
    GRIDPACK=sys.argv[3]

#print(FRAGMENT)

fragment_path = "Configuration/GenProduction/python"
if not os.path.exists(fragment_path):
    os.makedirs(fragment_path)

HEADER = """
SLHA_TABLE = '''
BLOCK MASS        # Mass Spectrum
#   PDG code   mass  particle
   1000001     5.00000000E+5   # ~d_L
   2000001     5.00000000E+5   # ~d_R
   1000002     5.00000000E+5   # ~u_L
   2000002     5.00000000E+5   # ~u_R
   1000003     5.00000000E+5   # ~s_L
   2000003     5.00000000E+5   # ~s_R
   1000004     5.00000000E+5   # ~c_L
   2000004     5.00000000E+5   # ~c_R
   1000005     5.00000000E+5   # ~b_1
   2000005     5.00000000E+5   # ~b_2
   1000006     5.00000000E+5   # ~t_1
   2000006     5.00000000E+5   # ~t_2
   1000011     5.00000000E+5   # ~e_L
   2000011     5.00000000E+5   # ~e_R
   1000012     5.00000000E+5   # ~nu_eL
   1000013     5.00000000E+5   # ~mu_L
   2000013     5.00000000E+5   # ~mu_R
   1000014     5.00000000E+5   # ~nu_muL
   1000015     5.00000000E+5   # ~tau_1
   2000015     5.00000000E+5   # ~tau_2
   1000016     5.00000000E+5   # ~nu_tauL
   1000021     {mass}          # ~g
   1000022     300   # ~chi_10
   1000023     300   # ~chi_20
   1000025     5.00000000E+5   # ~chi_30
   1000035     5.00000000E+5   # ~chi_40
   1000024     5.00000000E+5   # ~chi_1+
   1000037     300   # ~chi_2+
'''

import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunesRun3ECM13p6TeV.PythiaCP5Settings_cfi import *
from Configuration.Generator.Pythia8PowhegEmissionVetoSettings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *
""".format(mass=MGLU)

LHEProducer = """
externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring('{gridpack}'),
    nEvents = cms.untracked.uint32(5000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    generateConcurrently = cms.untracked.bool(True),
    #postGenerationCommand = cms.untracked.vstring('mergeLHE.py', '-i', 'thread*/cmsgrid_final.lhe', '-o', 'cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)
""".format(gridpack=GRIDPACK)


Hadronizer = """
generator = cms.EDFilter("Pythia8ConcurrentHadronizerFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    SLHATableForPythia8 = cms.string(SLHA_TABLE),
    comEnergy = cms.double(13600.),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        processParameters = cms.vstring(
            'SUSY:gg2gluinogluino = on', # Pair production of gluinos by gluon-gluon initial states (default = off)
            'SUSY:qqbar2gluinogluino = on', # (default = off)
            'SUSY:idA = 1000021',
            'SUSY:idB = 1000021',
            'JetMatching:scheme = 1',
            'JetMatching:merge = on',
            'JetMatching:jetAlgorithm = 2',
            'JetMatching:etaJetMax = 5.',
            'JetMatching:coneRadius = 1.',
            'JetMatching:slowJetPower = 1',
            'JetMatching:qCut = 10.', #this is the actual merging scale  (default = 10.0; minimum = 0.0)
            'JetMatching:clFact = 1', # determines jet-to parton matching  (default = 1.0)
            'JetMatching:nQmatch = 5', #5 for 5-flavour scheme (default = 5; minimum = 3; maximum = 6)
            'JetMatching:nJetMax = -1', #number of partons in born matrix element for highest multiplicity  (default = -1; minimum = -1)
            'JetMatching:doShowerKt = off',
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'pythia8PSweightsSettings',
                                    'processParameters',
                                    )
    )
)
"""

fragment_content = HEADER + LHEProducer + Hadronizer
if StartFromLHE:
    fragment_content = HEADER + Hadronizer

fi = open('{}/{}'.format(fragment_path,FRAGMENT),'w')

fi.write(fragment_content)

fi.close()