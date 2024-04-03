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

if args.clean:
    print (f'rm {args.outpath}/**/bb.log')
    os.system(f'/bin/bash -c "shopt -s globstar; rm -rf {args.outpath}/**/checkpoints"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.outpath}/**/checkpoints.done"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.outpath}/**/checkpoints.log"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.outpath}/**/checkpoints.stdout"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.outpath}/**/checkpoints.stderr"')
    sys.exit()

#Construct list of commands to be executed in parallel
commands = []
sppaths = glob.glob(args.simpointdir + "/**/simpoints.done", recursive=True)
benchexepaths = glob.glob(args.minispecdir + "/**/*.mytest-m64", recursive=True)

#Emit command for each simpoint path
for sppath in sppaths:
    spdir ='/'.join(sppath.split('/')[:-1])
    spname = sppath.split('/')[-3]
    spidx = int(sppath.split('/')[-2])

    #Skip generating clusters if issues present
    if os.path.exists(spdir + '/checkpoints.done'):
        with open(spdir + '/checkpoints.done', 'r') as exitcode:
            if int(exitcode.read().strip()) == 0:
                print(f'Skipped {spdir} (Checkpoints.done with code 0)')
                continue
    
    if os.path.exists(spdir + '/simpoints.done'):
        with open(spdir + '/simpoints.done', 'r') as exitcode:
            if int(exitcode.read().strip()) != 0:
                print(f'Skipped {spdir} (simpoint.done with non-zero exit code)')
                continue
    else:
        print(f'Skipped {spdir} (simpoint.done doesnt exist)')
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
    command.extend([f'{args.gem5dir}/build/X86/gem5.opt', f'--outdir={spdir}/checkpoints', f'{args.gem5dir}/configs/example/se.py',
                    '--cpu-type=X86KvmCPU',
                    f'--take-simpoint-checkpoint={spdir}/simpoints.simpts,{spdir}/simpoints.weights,{args.interval},{args.warmup}',
                    '-c', f'{benchexepath}',
                    f'--options="{benchopts}"',
                    f'--mem-size={args.memsize}GB'])
    
    if benchinfile is not None:
        command.extend(['--input', f'{args.minispecdir}/{spname}/{benchinfile}'])
    
    commands.append((spdir, command))

#Function for single blocking program call
def run_command(command_tuple):
    spdir, command = command_tuple

    print(f"Running {spdir}")

    with open(spdir + "/checkpoints.log", 'w+') as log:
        log.write(' '.join(command))
        process = subprocess.Popen(command, stdout=log, stderr=log)
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