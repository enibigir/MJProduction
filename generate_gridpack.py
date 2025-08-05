#!/usr/bin/env python
import os
import sys
import pathlib
import argparse
import time
import getpass

'''
Run for details
python3 generate_gridpack.py -h
'''

tarball_prefix='_tarball.tar.xz'

EXEC_NAME="temp_exec"
LOGS_NAME="temp_logs"
RUNS_NAME="temp_runs"

WORK_DIR=os.getcwd()

class ArgumentParser(argparse.ArgumentParser):
  def __init__(self):
    argparse.ArgumentParser.__init__(self, usage="%(prog)s <action> <command file> [options]")
    self.add_argument("--tag"         , dest="tag"       , type=str           , default='Run2023' , help="An identifier of the run, please take into account that the code will rewrite files by default, so change tag accordingly")
    self.add_argument("-f","--force"  , dest="force"     , action="store_true", default=False , help="Force the overwrite of temp folder and just overall ignore warnings.")
    self.add_argument("-o","--out"    , dest="out"       , type=str           , default=WORK_DIR, help="Output folder for gridpacks, default is current working directory (make sure you have dedicated space)")
    self.add_argument("-i","--in"     , dest="inF"       , type=str           , default=None, help="Input folder with the cards")
    self.add_argument("-q","--queue"  , dest="queue"     , type=str           , default="tomorrow", help="Condor queue to be used. Default is tomorrow (1 day). Other logical options are testmatch (3 days), nextweek (1 week), workday (8 hours)" )
    self.add_argument("-j","--jobs"   , dest="jobs"      , type=int           , default="4", help="Request this number of cores per job" )
    self.add_argument("-m","--memory" , dest="memory"    , type=int           , default="8000", help="Request memory in megabytes" )
    self.add_argument("-p","--pretend", dest="pretend"   , action="store_true", default=False , help="Only create folders and job scripts, don't run anything")
    self.add_argument("-l","--local",   dest="local"     , action="store_true", default=False , help="Only create local run folders, don't run anything")
    self.add_argument("-n", "--nevents",dest="nevents"   , type=int           , default=2000,   help="GRIDPACK_NEVENTS")

def pprint(t=""):
    print(f'[MJ] {t}') if t else print()

def create_submit_file(process, cards, jobs, mem, queue, exec_dir, logs_dir):
  submit_file = 'submit.sub'
  with open(submit_file,'w') as fi:
    fi.write("""#
executable              = $(filename)
arguments               = $(ClusterId)$(ProcId)
transfer_input_files    = {CARDS}
output                  = {LOGSDIR}/{PROCESS}_$(ClusterId).$(ProcId).out
error                   = {LOGSDIR}/{PROCESS}_$(ClusterId).$(ProcId).err
log                     = {LOGSDIR}/{PROCESS}_$(ClusterId).log
request_cpus            = {JOBS}
request_memory          = {MEMORY}
+JobFlavour             = "{QUEUE}"
## +MaxRuntime          = 2000000

queue filename matching ({EXECDIR}/job_{PROCESS}.sh)
""".format(PROCESS=process, CARDS=cards, EXECDIR=exec_dir, LOGSDIR=logs_dir, JOBS=jobs, MEMORY=mem, QUEUE=queue))
    fi.close()


def create_exec_file(process, nevents, cardsdir, outdir, exec_dir, logs_dir, local):
  exec_file = '{}/job_{}.sh'.format(exec_dir, process)

  LocalScript="true" if local else "false"

  with open(exec_file,'w') as fi:
    fi.write("""#!/bin/sh
echo ""
echo "Starting job on `date` at `hostname`"
echo "Running on: `cat /etc/redhat-release`"
echo ""
workarea=$PWD
LOCAL="{LOCAL}"
# First we do a sparse checkout of genproductions to avoid copying the whole thing and to also have the latests set of patches available
# We might want to fix a commit sha here to ensure it doesn't pull some tricks
git clone https://github.com/cms-sw/genproductions.git --no-checkout genproductions --depth 1
cd genproductions
git config core.sparsecheckout true
echo Utilities/scripts/ >> .git/info/sparse-checkout
echo MetaData >> .git/info/sparse-checkout
echo bin/MadGraph5_aMCatNLO >> .git/info/sparse-checkout
git read-tree -m -u HEAD
git apply {WORKDIR}/patch/set_gridpack_nevents.patch
cd bin/MadGraph5_aMCatNLO/

echo ""
echo "Entering '$PWD'"
echo ""

# Copy input cards
#echo "Copy input cards from: {CARDSDIR}"
#ls {CARDSDIR}

#cp -r {CARDSDIR} ./cards/
#xrdcp -r {CARDSDIR} ./cards/

# Create cards
mkdir cards/{PROCESS}
if $LOCAL; then
  cp {CARDSDIR}/{PROCESS}*.dat cards/{PROCESS}/
else
  cp $workarea/{PROCESS}*.dat cards/{PROCESS}/
fi
echo "./cards/{PROCESS}/:"
ls cards/{PROCESS}/


echo ""
if [ ! -d cards/{PROCESS} ]; then echo "ERROR: cards/{PROCESS} does NOT exist"
else
  #Run the script
  export GRIDPACK_NEVENTS={NEVENTS}
  sh gridpack_generation.sh {PROCESS} cards/{PROCESS}
  #Copy the gridpack back to somewhere readable
  mv {PROCESS}*.tar.xz {OUTDIR}/
  mv {PROCESS}.log {WORKDIR}/{LOGSDIR}/
fi

sleep 3
#Do some cleanup just to be tidy
cd ../../../
ls
rm -rf genproductions
""".format(CARDSDIR=cardsdir, PROCESS=process, NEVENTS=nevents, OUTDIR=outdir, LOGSDIR=logs_dir, WORKDIR=WORK_DIR, LOCAL=LocalScript))

  return exec_file

def get_cards(path, absolute_path=False):
  files = os.listdir('{}'.format(path))
  if absolute_path:
    files = [f'{path}/{f}' for f in files]
  return ','.join(files)


def create_dirs(TAG, LOCAL):
  exec_dir='{}_{}'.format(EXEC_NAME, TAG)
  logs_dir='{}_{}'.format(LOGS_NAME, TAG)
  runs_dir='{}_{}'.format(RUNS_NAME, TAG)

  if not (os.path.isdir(exec_dir) or os.path.isdir(logs_dir)):
    pprint('Creating directories ...')
    os.system("mkdir {}".format(exec_dir))
    os.system("mkdir {}".format(logs_dir))
    pprint('Done!')
  if (not os.path.isdir(runs_dir)) and LOCAL:
    pprint('Creating Run directory ...')
    os.system("mkdir {}".format(runs_dir))
    if not os.path.isdir(logs_dir):
      os.system("mkdir {}".format(logs_dir))
    pprint('Done!')

  return exec_dir,logs_dir,runs_dir

##################################################################################################
##################################################################################################
if __name__ == "__main__":
  args = ArgumentParser().parse_args()

  process_name=args.inF.split('/')[-1]

  pprint(f'Process: {process_name}')

  # exit()

  exec_dir,logs_dir,runs_dir = create_dirs(args.tag, args.local)

  if "/afs/" in args.out and not(args.force):
    raise RuntimeError("Error: you are sending your final gridpacks to be copied to afs, this might be a bad idea unless you have dedicated space for them. Run with force mode (-f) to force this.")
  if os.path.isdir(exec_dir) and not(args.force):
    raise RuntimeError("Error: {} already exist. Run with force mode (-f) to force this.".format(exec_dir))
  if not(os.path.isdir(args.out)) and not ('root://' in args.out):
    os.system("mkdir {}".format(args.out))


  ##### creating and sending jobs #####
  EXECFILE=create_exec_file(process_name, args.nevents, args.inF, args.out, exec_dir, logs_dir, args.local)

  os.system("chmod 755 {}".format(EXECFILE))

  cards = get_cards(args.inF, True)

  if args.local:
    os.system('cp {} {}/'.format(EXECFILE, runs_dir))
  else:
    create_submit_file(process_name, cards, args.jobs, args.memory, args.queue, exec_dir, logs_dir)

    ###### sends bjobs ######
    if not args.pretend:
      os.system("echo submit.sub")
      time.sleep(3)
      os.system("condor_submit submit.sub")
      
      pprint()
      pprint("Your jobs are here:")
      os.system("condor_q")
      pprint()
      pprint('END')
      pprint()