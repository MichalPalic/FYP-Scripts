import argparse
import os
import sys
import glob
from workload_coremarkpro import *
import multiprocessing
import subprocess

parser = argparse.ArgumentParser(
                prog='Coremarkpro run script',
                description='Runs sub-benchmarks in parallel through gem5 O3')


parser.add_argument('--gem5dir',
                type=str,
                default="/home/michal/Desktop/gem5_stable",
                help='Path to gem5 executable to be used')

parser.add_argument('--coremarkprodir',
                type=str,
                default="/home/michal/Desktop/coremark-pro",
                help='Path to gem5 executable to be used')

parser.add_argument('--resultdir',
                type=str,
                default="/home/michal/Desktop/coremarkpro_results_gcc_10",
                help='Path to input/output directory')

parser.add_argument('-j', '--jobs',
                type=int,
                default=multiprocessing.cpu_count(),
                help='Number of jobs to run in parallel')

parser.add_argument('-c', '--clean',
                action='store_true',
                default=False,
                help='Clean existing ')

args = parser.parse_args()

#Ensure absolute paths
args.gem5dir = os.path.abspath(args.gem5dir)

if args.clean:
    os.system(f'/bin/bash -c "shopt -s globstar; rm -rf {args.resultdir}/**/checkpoints"')
    print (f'Cleaned result dir')
    sys.exit()

#Construct list of commands to be executed in parallel
commands = []

#Emit command for each simpoint path
for workload_name in workloads:
    result_dir = f"{args.resultdir}/{workload_name}"

    #Skip generating command if already run to completion
    if os.path.exists(result_dir + '/run.done'):
        with open(result_dir + '/run.done', 'r') as exitcode:
            if int(exitcode.read().strip()) == 0:
                print(f'Skipped {result_dir} (run.done with code 0)')
                continue

    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    workload_path = f"{args.coremarkprodir}/builds/linux64/gcc64/bin/{workloads[workload_name].name}"
    benchopts = ' '.join(workloads[workload_name].args[0])
    
    command = []
    command.extend([f'{args.gem5dir}/build/X86/gem5.debug', f'--outdir={result_dir}', f'{args.gem5dir}/configs/example/se.py',
                    '--cpu-type=X86O3CPU',
                    '--caches',
                    '-c', f'{workload_path}',
                    f'--options="{benchopts}"',
                    f'--mem-size=8GB'])
    
    commands.append((result_dir, command))

#Function for single blocking program call
def run_command(command_tuple):
    result_dir, command = command_tuple

    print(f"Running {result_dir}")

    with open(result_dir + "/run.log", 'w+') as log:
        log.write(' '.join(command))
        process = subprocess.Popen(command, stdout=log, stderr=log)
        (output, err) = process.communicate()  
        p_status = process.wait()
    

    with open(result_dir + "/run.done", 'w+') as statusf:
        statusf.write(str(p_status))
    
    print(f"Finished {result_dir} with exit code {p_status}")
        
#Execute commands in parallel with pool
pool = multiprocessing.Pool(args.jobs)

with pool:
    pool.map(run_command, commands)

print("Done")