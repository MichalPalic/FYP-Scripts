import argparse
import os
import sys
from workloads import *
import multiprocessing
import subprocess


parser = argparse.ArgumentParser(
                prog='Valgrind BBV Config Script',
                description='Generate Basic Block Vectors for Simpoints clustering')

parser.add_argument('--interval',
                type=int,
                default=10**7,
                help='Set simpoints interval duration in instructions')

parser.add_argument('--minispec',
                type=str,
                default="/home/michal/Desktop/MINISPEC2017",
                help='Path to compiled "Mini"SPEC (Extracted executables and input files)')

parser.add_argument('--outpath',
                type=str,
                default="/home/michal/Desktop/SPEC2017SIM",
                help='Output path for saving bbvectors')

parser.add_argument('-n', '--nthreads',
                type=int,
                default=16,
                help='Number of jobs to run in parallel')

parser.add_argument('--clean',
                action='store_true',
                default=False,
                help='Clean existing bbvs')

args = parser.parse_args()

#Additional input validation
if not os.path.exists(args.minispec):
    print("Minispec path does not exist")
    sys.exit()

if not os.path.isdir(args.minispec):
    print("Minispec not a directory")
    sys.exit()

args.minispec = os.path.abspath(args.minispec)
args.outpath = os.path.abspath(args.outpath)

if args.clean:
    print (f'rm {args.outpath}/**/bb.log')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.outpath}/**/bb.log"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.outpath}/**/bb.txt"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.outpath}/**/bb.done"')
    sys.exit()

#Read benchmarks in minispec folder
entries = os.listdir(args.minispec)
folders = [folder for folder in entries if os.path.isdir(args.minispec+ '/' + folder)]

#Construct list of commands to be executed in parallel
commands = []

for folder in folders:
    benchmark = workloads[folder]
    for idx, benchmark_args in enumerate(benchmark.args):
        command = []

        #Create missing output directory 
        outdir = args.outpath + '/' + folder + f'/{idx}'

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        #Skip generating bbv for this item if already generated with zero exit code
        if os.path.exists(outdir + '/bb.done'):
            with open(outdir + "/bb.done", 'r') as exitcode:
                if int(exitcode.read()) == 0:
                    print(f'Skipped {outdir}')
                    pass

        #Construct executable path according to weird SPEC semi-convention
        programname = folder.split('.')[1]
        programdir = args.minispec + '/' + folder
        programpath = programdir + '/' + programname + '_base.mytest-m64'

        assert os.path.isfile(programpath), f"Failed to infer executable path: {programpath}"

        command.extend(['valgrind',  '--tool=exp-bbv', f'--interval-size={args.interval}',
                        f'--bb-out-file={outdir}/bb.txt', f'{programpath}' ])
        command.extend(benchmark_args)

        commands.append((programdir, outdir, benchmark.std_inputs, command))

#Function for single blocking program call
def run_command(command_tuple):
    programdir, outdir, inpath, command = command_tuple

    print(f"Running {programdir}")

    os.chdir(programdir)
    with open(outdir + "/bb.log", 'w+') as log:
        log.write(' '.join(command))

        if inpath is not None:
            infile = open(inpath, 'r')
        else:
            infile = None

        process = subprocess.Popen(command, stdout=log, stderr=log, stdin=infile)
        (output, err) = process.communicate()  
        p_status = process.wait()

    with open(outdir + "/bb.done", 'w+') as statusf:
        statusf.write(str(p_status))

    print(f"Finished {programdir} with exit code {p_status}")

        
#Execute commands in parallel
pool = multiprocessing.Pool(args.nthreads)

with pool:
    pool.map(run_command, commands)

print("Done")