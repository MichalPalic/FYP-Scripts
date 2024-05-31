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
                default="/home/michal/Desktop/gem5_oracle",
                help='Path to gem5 executable to be used')

parser.add_argument('--coremarkprodir',
                type=str,
                default="/home/michal/Desktop/coremark-pro",
                help='Path to gem5 executable to be used')

parser.add_argument('--resultdir',
                type=str,
                default="/home/michal/Desktop/coremarkpro_trace_result",
                help='Path to input/output directory')

parser.add_argument('--trace_dir',
                type=str,
                default="/home/michal/Desktop/coremarkpro_trace",
                help='Directory containing/to to contain trace')

parser.add_argument('-j', '--jobs',
                type=int,
                default=multiprocessing.cpu_count(),
                help='Number of jobs to run in parallel')

parser.add_argument('--gen_trace',
                action='store_true',
                default=False,
                help='Generate oracle trace')

parser.add_argument('--run_trace',
                action='store_true',
                default=False,
                help='Use trace to run workload with oracle')

parser.add_argument('--debug',
                action='store_true',
                default=False,
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
    
    trace_dir = f"{args.trace_dir}/{workload_name}"
    if not os.path.exists(trace_dir):
        os.makedirs(trace_dir)

    workload_path = f"{args.coremarkprodir}/builds/linux64/gcc64/bin/{workloads[workload_name].name}"
    benchopts = ' '.join(workloads[workload_name].args[0])
    
    command = []
    command.extend([f'{args.gem5dir}/build/X86/gem5' + ('.debug' if args.debug
                    else '.opt'), f'--outdir={result_dir}',
                    #"--debug-flags=FYPDebug,MemOracle",
                    f'{args.gem5dir}/configs/deprecated/example/se.py',
                    '-c', f'{workload_path}',
                    f'--options={benchopts}',
                    f'--mem-size=8GB',

                    #Luke XL params
                    '--cpu-type=X86O3CPU',
                    '--caches',
                    '--l2cache',
                    '--l1d_size=256KiB',
                    '--l1i_size=256KiB',
                    '--l2_size=4MB'])

    commands.append((result_dir, trace_dir, command))

#Function for single blocking program call
def run_command(command_tuple):
    result_dir, trace_dir, command = command_tuple

    #Create modified environment if tracing enabled
    my_env = os.environ.copy()
    
    if (args.gen_trace):
        my_env["ORACLEMODE"] = "Trace"
    elif (args.run_trace):
        my_env["ORACLEMODE"] = "Refine"
        
    if (args.gen_trace or args.run_trace):
        my_env["TRACEDIR"] = trace_dir


    print(f"Running {result_dir}")

    with open(result_dir + "/run.log", 'w+') as log:
        log.write(' '.join(command))
        process = subprocess.Popen(command, stdout=log, stderr=log, env=my_env)
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