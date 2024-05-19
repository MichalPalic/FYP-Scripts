#Example command run for tracer
#python3 coremarkpro_scripts/run_coremarkpro.py --gen_trace --resultdir /home/michal/Desktop/coremarkpro_trace_gcc_10 --gem5dir /home/michal/Desktop/gem5_oracle_tracer -j 1 --debug

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
                default="/home/michal/Desktop/coremarkpro_store_set_sweep",
                help='Path to input/output directory')

parser.add_argument('-j', '--jobs',
                type=int,
                default=multiprocessing.cpu_count(),
                help='Number of jobs to run in parallel')

parser.add_argument('--debug',
                action='store_true',
                default=True,
                help='Use gem5 .debug build instead of .opt')

parser.add_argument('-c', '--clean',
                action='store_true',
                default=False,
                help='Clean existing ')

args = parser.parse_args()

#Ensure absolute paths
args.gem5dir = os.path.abspath(args.gem5dir)

if args.clean:
    # os.system(f'/bin/bash -c "shopt -s globstar; rm -rf {args.resultdir}/**/checkpoints"')
    # print (f'Cleaned result dir')
    sys.exit()

#Construct list of commands to be executed in parallel
commands = []

for ssit in [192, 256, 512, 1024, 2048, 4096]:
    for lfst in [192, 256, 512, 1024, 2048, 4096]:

        #Add 192, 192 datapoint
        if (ssit == 192 or lfst == 192) and lfst != ssit:
            continue

        #Proportional to number of entries
        clear_period = (62464 // (192 + 192)) * (ssit + lfst)

        #Emit command for each simpoint path
        for workload_name in workloads:
            result_dir = f"{args.resultdir}/{ssit}_{lfst}/{workload_name}"

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
                            else '.opt'), f'--outdir={result_dir}', f'{args.gem5dir}/configs/example/se.py',
                            '-c', f'{workload_path}',
                            f'--options="{benchopts}"',
                            f'--mem-size=8GB',

                            #Luke XL params
                            '--cpu-type=X86O3CPU',
                            '--caches',
                            '--l2cache',
                            '--l1d_size=256KiB',
                            '--l1i_size=256KiB',
                            '--l2_size=4MB',
                            f"--lfst-size={lfst}",
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