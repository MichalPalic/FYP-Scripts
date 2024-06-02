#The checkpoints contain absolute paths in .cpt file descriptor array.
#This means that about 10% of checkpoints will error out with exit code
#1 if they are run in a different directory structure because of files not found.
#This script should be run with an updated spec executable location after checkpoints are extracted.
#Note that it looks for a specific path in the checkpoints, so it will have no effect if run a second time

import argparse
import os
import glob

parser = argparse.ArgumentParser(
                prog='Checkpoint fix script',
                description='Generate Basic Block Vectors for Simpoints clustering')

parser.add_argument('--specexedir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_executables",
                help='Path to minispec directory)')

parser.add_argument('--checkpointdir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_checkpoints",
                help='Path to input/output directory)')

args = parser.parse_args()

#Ensure absolute paths without trailing /
args.checkpointdir = os.path.abspath(args.checkpointdir)
if args.checkpointdir[-1] == '/':
    args.checkpointdir = args.checkpointdir[:-1]

args.specexedir = os.path.abspath(args.specexedir)
if args.specexedir[-1] == '/':
    args.specexedir = args.specexedir[:-1]

#Construct list of commands to be executed in parallel
commands = []
checkpoint_paths = glob.glob(args.checkpointdir + "/**/m5.cpt", recursive=True)

old_path = "/homehdd/michal/Desktop/spec_2017_rate_executables"

for checkpoint_path in checkpoint_paths:

    with open(checkpoint_path, 'r') as file: 
        data = file.read() 
        data = data.replace(old_path, args.specexedir)
         
    with open(checkpoint_path, 'w') as file: 
        file.write(data) 