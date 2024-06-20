import argparse
import os
import sys
import glob
from workload_spec import *
import multiprocessing
import subprocess

#If you're getting -6 exit codes, you need to do some system side setup!
#echo "-1" | sudo tee /proc/sys/kernel/perf_event_paranoid
#https://www.gem5.org/documentation/general_docs/using_kvm/

parser = argparse.ArgumentParser(
                prog='Kvm Checkpoint generation Script',
                description='Generate checkpoints from SimPoint descriptors')

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
                default="/home/michal/Desktop/gem5_develop",
                help='Path gem5 directory')

parser.add_argument('--workdir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_checkpoints",
                help='Path to input/output directory')

parser.add_argument('--specexe',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_executables",
                help='Path to minispec directory)')

parser.add_argument('-j', '--jobs',
                type=int,
                default=os.cpu_count(),
                help='Number of jobs to run in parallel')


parser.add_argument('-m', '--memsize',
                type=int,
                default=16,
                help='Maximum memory size')


parser.add_argument('--debug',
                action='store_true',
                default=False,
                help='Use gem5 .debug build instead of .opt')

parser.add_argument('--clean',
                action='store_true',
                default=False,
                help='Clean existing ')

args = parser.parse_args()

#Ensure absolute paths
args.workdir = os.path.abspath(args.workdir)
args.specexe = os.path.abspath(args.specexe)

if args.clean:
    os.system(f'/bin/bash -c "shopt -s globstar; rm -rf {args.workdir}/**/checkpoints"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.workdir}/**/checkpoints.done"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.workdir}/**/checkpoints.log"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.workdir}/**/checkpoints.stdout"')
    os.system(f'/bin/bash -c "shopt -s globstar; rm {args.workdir}/**/checkpoints.stderr"')
    print (f'Checkpoints cleaned')
    sys.exit()

#Construct list of commands to be executed in parallel
commands = []
sppaths = glob.glob(args.workdir + "/**/simpoints.done", recursive=True)
benchexepaths = glob.glob(args.specexe + "/**/*.mytest-m64", recursive=True)

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
    benchexepath = f'{args.specexe}/{spname}/{benchexename}_base.mytest-m64'
    benchexedir = f'{args.specexe}/{spname}'

    if not os.path.exists(f'{spdir}/checkpoints'):
        os.makedirs(f'{spdir}/checkpoints')

    command = []
    command.extend([f'{args.gem5dir}/build/X86/gem5' + ('.debug' if args.debug
                    else '.opt'), 
                    f'--outdir={spdir}/checkpoints', 
                    f'{args.gem5dir}/configs/deprecated/example/se.py',
                    '--cpu-type=X86KvmCPU',

                    f'--take-simpoint-checkpoint={spdir}/simpoints.simpts,{spdir}/simpoints.weights,{args.interval},{args.warmup}',
                    f'--cmd={benchexepath}',
                    f'--options={benchopts}',
                    f'--mem-size={args.memsize}GB'])

    if benchinfile is not None:
        command.extend(['--input', f'{args.specexe}/{spname}/{benchinfile}'])

    commands.append((spdir, benchexedir, command))

    print(' '.join(commands[-1][-1]))

#Function for single blocking program call
def run_command(command_tuple):
    spdir, benchexedir, command = command_tuple

    print(f"Running {spdir}")

    with open(spdir + "/checkpoints.log", 'w+') as log:
        
        process = subprocess.Popen(command, stdout=log, stderr=log, cwd=benchexedir)
        (output, err) = process.communicate()  
        p_status = process.wait()


    with open(spdir + "/checkpoints.done", 'w+') as statusf:
        statusf.write(str(p_status))

    print(f"Finished {spdir} with exit code {p_status}")

#Execute commands in parallel with pool
pool = multiprocessing.Pool(args.jobs)

with pool:
    pool.map(run_command, commands)

print("Done")