import argparse
import os
import sys
from workload_spec import *
import multiprocessing
import subprocess
from datetime import datetime

parser = argparse.ArgumentParser(
                prog='Valgrind BBV Config Script',
                description='Generate Basic Block Vectors for Simpoints clustering')

parser.add_argument('--interval',
                type=int,
                default=10**7,
                help='Set simpoints interval duration in instructions')

parser.add_argument('--specexe',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_executables",
                help='Path to structured compiled extracted executables and input files')

parser.add_argument('--workdir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_checkpoints",
                help='Output path for saving bbvectors')

parser.add_argument('-j', '--jobs',
                type=int,
                default=os.cpu_count(),
                help='Number of jobs to run in parallel')

parser.add_argument('--clean',
                action='store_true',
                default=False,
                help='Clean existing bbvs')

args = parser.parse_args()

#Additional input validation
if not os.path.exists(args.specexe):
    print("specexe path does not exist")
    sys.exit()


args.specexe = os.path.abspath(args.specexe)
args.workdir = os.path.abspath(args.workdir)

if args.clean:
    print (f'rm {args.workdir}/**/bb.log')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.workdir}/**/bb.log"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.workdir}/**/bb.txt"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.workdir}/**/bb.done"')
    sys.exit()

#Read benchmarks in specexe folder
entries = os.listdir(args.specexe)
folders = [folder for folder in entries if os.path.isdir(args.specexe+ '/' + folder)]
folders.sort()

#Construct list of commands to be executed in parallel
commands = []

for folder in folders:
    benchmark = workloads[folder]
    for idx, benchmark_args in enumerate(benchmark.args):
        command = []

        #Create missing output directory 
        outdir = args.workdir + '/' + folder + f'/{idx}'

        if not os.path.exists(outdir):
            os.makedirs(outdir)

        #Skip generating bbv for this item if already generated with zero exit code
        if os.path.exists(outdir + '/bb.done'):
            with open(outdir + "/bb.done", 'r') as exitcode:
                if int(exitcode.read()) == 0:
                    print(f'Skipped {outdir} (bb.done with zero exit code)')
                    continue

        #Construct executable path according to weird SPEC semi-convention
        programname = folder.split('.')[1]
        programdir = args.specexe + '/' + folder
        programpath = programdir + '/' + programname + '_base.mytest-m64'

        assert os.path.isfile(programpath), f"Failed to infer executable path: {programpath}"

        command.extend(['valgrind',
                        '--tool=exp-bbv',
                        f'--interval-size={args.interval}',
                        f'--bb-out-file={outdir}/bb.txt',
                        f'{programpath}' ])
        
        command.extend(benchmark_args)

        if benchmark.std_inputs is not None:
            stdin_path = benchmark.std_inputs[idx]
        else:
            stdin_path = None

        commands.append((programdir, outdir, stdin_path, command))

#Function for single blocking program call
def run_command(command_tuple):
    programdir, outdir, inpath, command = command_tuple

    current_datetime = datetime.now()

    print(f"{current_datetime.timestamp()}: Running {outdir}")

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

    print(f"{current_datetime.timestamp()}: Finished {outdir} with exit code {p_status}")

        
#Execute commands in parallel
pool = multiprocessing.Pool(args.jobs)

with pool:
    pool.map(run_command, commands)

print("Done")