import argparse
import os
import sys
import glob
from workload_spec import *
import multiprocessing
import subprocess
import time
import random

#If you're getting -6 exit codes, you need to do some system side setup!
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
                default="/home/michal/Desktop/gem5_stable",
                help='Path gem5 directory')

parser.add_argument('--workdir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_checkpoints",
                help='Path to input/output directory')

parser.add_argument('--specdir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_executables",
                help='Path to minispec directory)')

parser.add_argument('-j', '--jobs',
                type=int,
                default=os.cpu_count(),
                help='Number of jobs to run in parallel')


parser.add_argument('-m', '--memsize',
                type=int,
                default=8,
                help='Maximum memory size')

parser.add_argument('--clean',
                action='store_true',
                default=False,
                help='Clean existing ')

parser.add_argument('--debug',
                action='store_true',
                default=False,
                help='Use gem5 .debug build instead of .opt')

parser.add_argument('--cpt-hack',
                action='store_true',
                default=False,
                help='Rename all "switch_cpu_1" references in .cpt files to "cpu".')

args = parser.parse_args()

#Ensure absolute paths
args.workdir = os.path.abspath(args.workdir)
args.specdir = os.path.abspath(args.specdir)

if(args.cpt_hack):
    #HACK: Rename serialised structures in checkpoint to enable proper loading
    os.system(f"""/bin/bash -c "shopt -s globstar; sed -i 's/switch_cpus_1/cpu/g' {args.workdir}/**/m5.cpt " """)
    sys.exit()

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
sppaths.sort()
benchexepaths = glob.glob(args.specdir + "/**/*.mytest-m64", recursive=True)

#Emit command for each simpoint path
for sppath in sppaths:
    spdir ='/'.join(sppath.split('/')[:-1])
    spname = sppath.split('/')[-3]
    spidx = int(sppath.split('/')[-2])

    #Check simpoint files
    if os.path.exists(spdir + '/simpoints.done') and os.path.exists(spdir + '/simpoints.simpts'):
        with open(spdir + '/simpoints.done', 'r') as exitcode:
            if int(exitcode.read().strip()) != 0:
                print(f'Skipped {spdir} (simpoint.done with non-zero exit code)')
                continue
    else:
        print(f'Skipped {spdir} (simpoint.done/simpoints.simpts doesnt exist)')
        pass
    
    #Get number of checkpoints
    with open(spdir + '/simpoints.simpts', 'r') as simpoints:
        n_checkpoints = len(simpoints.readlines())
        print(f'Found {n_checkpoints} simpoint intervals for {spdir}')
    
    for checkpoint_idx in range(n_checkpoints):

        #Skip generating clusters if this checkpoint already generated
        if os.path.exists(spdir + '/checkpoints.done'):
            with open(spdir + '/checkpoints.done', 'r') as checkpoints_done:
                done_checkpoints = checkpoints_done.read().split(' ')
                if str(checkpoint_idx) in done_checkpoints:
                    print(f'Skipped {spdir} CP: {checkpoint_idx} (Checkpoints.done contains checkpoint with code 0)')
                    continue

        benchexepath = [x for x in benchexepaths if spname in x][0]

        benchopts = ' '.join(workloads[spname].args[spidx])

        if workloads[spname].std_inputs is not None:
            benchinfile = workloads[spname].std_inputs[spidx]
        else:
            benchinfile = None

        benchexename = spname.split('.')[1] 
        benchexepath = f'{args.specdir}/{spname}/{benchexename}_base.mytest-m64'
        benchexedir = f'{args.specdir}/{spname}'

        if not os.path.exists(f'{spdir}/checkpoints'):
            os.makedirs(f'{spdir}/checkpoints')
        
        command = []
        command.extend([f'{args.gem5dir}/build/X86/gem5' + ('.debug' if args.debug
                    else '.opt'), 
                        f'--outdir={spdir}/checkpoints', 
                        f'{args.gem5dir}/configs/example/se.py',
                        '--cpu-type=X86KvmCPU',
                        
                        #My hacked SE script to switch from Kvm cpu before taking CP
                        '--checkpoint-with-cpu=X86AtomicSimpleCPU',

                        #Simpoints 1 indexed
                        f'--checkpoint-with-cpu-n={checkpoint_idx + 1}',  

                        f'--take-simpoint-checkpoint={spdir}/simpoints.simpts,{spdir}/simpoints.weights,{args.interval},{args.warmup}',
                        f'--cmd={benchexepath}',
                        f'--options={benchopts}',
                        f'--mem-size={args.memsize}GB'])
        
        if benchinfile is not None:
            command.extend(['--input', f'{args.specdir}/{spname}/{benchinfile}'])
        
        commands.append((spdir, benchexedir, command, checkpoint_idx))

#Function for single blocking program call
def run_command(command_tuple):
    spdir, benchexedir, command, checkpoint_idx = command_tuple

    #Something seems to be causing problems with file access at the same time
    #Add random delay to prevent clashes
    time.sleep(random.randint(0, 20))

    print(f"Running {spdir} CP:{checkpoint_idx}")

    with open(spdir  + f"/checkpoints/checkpoints{checkpoint_idx}.log", 'w+') as log:
        log.write(' '.join(command))
        process = subprocess.Popen(command, stdout=log, stderr=log, cwd=benchexedir)
        (output, err) = process.communicate()  
        p_status = process.wait()
    
    # if os.path.exists(spdir + '/checkpoints.done'):

    if(p_status == 0):
        with open(spdir + "/checkpoints.done", 'a+') as statusf:
            statusf.write(str(checkpoint_idx) + " ")
    
    print(f"Finished {spdir} CP:{checkpoint_idx} with exit code {p_status}")
        
#Execute commands in parallel with pool
pool = multiprocessing.Pool(args.jobs)

with pool:
    pool.map(run_command, commands)

print("Done Running; Applying checkpoint HACK")

#HACK: Rename serialised structures in checkpoint to enable proper loading
os.system(f"""/bin/bash -c "shopt -s globstar; sed -i 's/switch_cpus_1/cpu/g' {args.workdir}/**/m5.cpt " """)

