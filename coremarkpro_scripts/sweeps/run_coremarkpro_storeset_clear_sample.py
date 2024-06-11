#Example command run for tracer
#python3 coremarkpro_scripts/run_coremarkpro.py --gen_trace --resultdir /home/michal/Desktop/coremarkpro_trace_gcc_10 --gem5dir /home/michal/Desktop/gem5_oracle_tracer -j 1 --debug

import argparse
import os
import sys
import glob
from ..workload_coremarkpro import *
import multiprocessing
import subprocess

parser = argparse.ArgumentParser(
                prog='Coremarkpro run script',
                description='Runs sub-benchmarks in parallel through gem5 O3')


parser.add_argument('--gem5dir',
                type=str,
                default="/vol/bitbucket/mp3120/gem5_develop",
                help='Path to gem5 executable to be used')

parser.add_argument('--coremarkprodir',
                type=str,
                default="/vol/bitbucket/mp3120/coremark-pro",
                help='Path to gem5 executable to be used')

parser.add_argument('--resultdir',
                type=str,
                default="/vol/bitbucket/mp3120/coremarkpro_clear_sweep_sample",
                help='Path to input/output directory')

parser.add_argument('-j', '--jobs',
                type=int,
                default=multiprocessing.cpu_count(),
                help='Number of jobs to run in parallel')

parser.add_argument('-m', '--machines',
                type=int,
                default=5,
                help='Number of machines to spread work across')

parser.add_argument('-c', '--machine_idx',
                type=int,
                default=1,
                help='Index of machine')

parser.add_argument('--debug',
                action='store_true',
                default=False,
                help='Use gem5 .debug build instead of .opt')

args = parser.parse_args()

#Ensure absolute paths
args.gem5dir = os.path.abspath(args.gem5dir)

#Construct list of commands to be executed in parallel
commands = []

ssitlist = [64, 512, 4096, 32768, 262144]
lfstlist = [64, 512, 4096, 32768, 262144]

clear_base = 1000000
clear_mult_list = [0.125, 0.25, 0.5, 1, 2, 4, 8]
    

for idx, ssit in enumerate(ssitlist) :
    if idx % args.machines != args.machine_idx:
        continue

    for lfst in lfstlist:
        for clear_mult in clear_mult_list:
            clear_period = int(clear_base * float(clear_mult))

            #Emit command for each simpoint path
            for workload_name in workloads:
                result_dir = f"{args.resultdir}/{ssit}_{lfst}_{clear_period}/{workload_name}"

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
                command.extend([f'{args.gem5dir}/build/X86/gem5' + ('.debug' if args.debug
                                else '.fast'), f'--outdir={result_dir}', f'{args.gem5dir}/configs/deprecated/example/se.py',
                                '-c', f'{workload_path}',
                                f'--options={benchopts}',
                                f'--mem-size=8GB',

                                #Luke XL params
                                '--cpu-type=X86O3CPU',
                                '--caches',
                                '--l2cache',
                                '--l1d_size=256KiB',
                                '--l1i_size=256KiB',
                                '--l2_size=4MB',
                                f"--lfst-size={ssit}",
                                f"--ssit-size={ssit}",
                                f"--store-set-clear-period={clear_period}",
                                ])

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