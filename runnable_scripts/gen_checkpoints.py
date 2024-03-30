import argparse
import os
import sys
import glob
from workload_spec import *
import multiprocessing
import subprocess

#Some setup
#echo "-1" | sudo tee /proc/sys/kernel/perf_event_paranoid
#https://www.gem5.org/documentation/general_docs/using_kvm/

parser = argparse.ArgumentParser(
                prog='Valgrind BBV Config Script',
                description='Generate Basic Block Vectors for Simpoints clustering')

parser.add_argument('--interval',
                type=int,
                default=10**7,
                help='Set simpoints interval duration in instructions')
parser.add_argument('--warmup',
                type=int,
                default=10**6,
                help='Set simpoints warmup duration in instructions')

parser.add_argument('--gem5dir',
                type=str,
                default="/home/michal/Desktop/gem5_michal",
                help='Path gem5 directory')

parser.add_argument('--simpointdir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_checkpoints",
                help='Path to input/output directory)')

parser.add_argument('--minispecdir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_executables",
                help='Path to minispec directory)')

parser.add_argument('-n', '--nthreads',
                type=int,
                default=2,
                help='Number of jobs to run in parallel')


parser.add_argument('-m', '--memsize',
                type=int,
                default=8,
                help='Maximum memory size')

parser.add_argument('--clean',
                action='store_true',
                default=False,
                help='Clean existing ')

args = parser.parse_args()

#Ensure absolute paths
args.simpointdir = os.path.abspath(args.simpointdir)
args.minispecdir = os.path.abspath(args.minispecdir)

#Construct list of commands to be executed in parallel
commands = []
sppaths = glob.glob(args.simpointdir + "/**/simpoints.simpts", recursive=True)
benchexepaths = glob.glob(args.minispecdir + "/**/*.mytest-m64", recursive=True)

#Emit command for each simpoint path
for sppath in sppaths:
    spdir ='/'.join(sppath.split('/')[:-1])
    spname = sppath.split('/')[-3]
    spidx = int(sppath.split('/')[-2])

    #Skip generating clusters for this item if already successfully generated
    if os.path.exists(spdir + '/checkpoints.done'):
        with open(spdir + '/checkpoints.done', 'r') as exitcode:
            if int(exitcode.read()) == 0:
                print(f'Skipped {spdir}')
                pass

    benchexepath = [x for x in benchexepaths if spname in x][0]

    benchopts = ' '.join(workloads[spname].args[spidx])
    if workloads[spname].std_inputs is not None:
        benchinfile = workloads[spname].std_inputs[spidx]
    else:
        benchinfile = None

    benchexename = spname.split('.')[1] 
    benchexepath = f'{args.minispecdir}/{spname}/{benchexename}_base.mytest-m64'

    if not os.path.exists(f'{spdir}/checkpoints'):
        os.makedirs(f'{spdir}/checkpoints')
    
    command = []
    command.extend([f'{args.gem5dir}/build/X86/gem5.opt', f'--outdir={spdir}/checkpoints', f'{args.gem5dir}/configs/deprecated/example/se.py',
                    '--cpu-type=X86KvmCPU',
                    f'--take-simpoint-checkpoint={spdir}/simpoints.simpts,{spdir}/simpoints.weights,{args.interval},{args.warmup}',
                    '-c', f'{benchexepath}',
                    f'--options="{benchopts}"',
                    '--output', f'{spdir}/checkpoints.log',
                    '--errout', f'{spdir}/checkpoints.log',
                    f'--mem-size={args.memsize}GB'])
    
    if benchinfile is not None:
        command.extend(['--input', benchinfile])
    
    commands.append((spdir, command))

#Function for single blocking program call
def run_command(command_tuple):
    spdir, command = command_tuple

    print(f"Running {spdir}")

    with open(spdir + "/checkpoints.log", 'w+') as log:
        log.write(' '.join(command))
        process = subprocess.Popen(command,) # stdout=, stderr=log
        (output, err) = process.communicate()  
        p_status = process.wait()
    

    with open(spdir + "/checkpoints.done", 'w+') as statusf:
        statusf.write(str(p_status))
    
    print(f"Finished {spdir} with exit code {p_status}")
        
#Execute commands in parallel with pool
pool = multiprocessing.Pool(args.nthreads)

with pool:
    pool.map(run_command, commands)

print("Done")