import argparse
import os
import sys
import glob
from workload_spec import *
import multiprocessing
import subprocess
from datetime import datetime


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
                default="/home/michal/Desktop/gem5_oracle",
                help='Path gem5 directory')

parser.add_argument('--checkpointdir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_checkpoints",
                help='Path to input/output directory)')

parser.add_argument('--resultdir',
                type=str,
                default="/home/michal/Desktop/windows/FYP/spec_2017_rate_sweep_depshift",
                help='Path to result directory')

parser.add_argument('--specexedir',
                type=str,
                default="/home/michal/Desktop/spec_2017_rate_executables",
                help='Path to minispec directory)')

parser.add_argument('-j', '--jobs',
                type=int,
                default=multiprocessing.cpu_count(),
                help='Number of jobs to run in parallel')

parser.add_argument('-m', '--memsize',
                type=int,
                default=16,
                help='Maximum memory size')

parser.add_argument('--debug',
                action='store_true',
                default=False,
                help='Use gem5 .debug build instead of .opt')

#Oracle options
parser.add_argument('--gen-trace',
                action='store_true',
                default=False,
                help='Generate oracle trace')

parser.add_argument('--refine-trace',
                action='store_true',
                default=False,
                help='Use trace to run and refine workload with oracle')

parser.add_argument('--trace-dir',
                type=str,
                default="/home/michal/Desktop/windows/FYP/spec_2017_rate_trace_r1",
                help='Directory containing/to to contain trace')

args = parser.parse_args()

#Ensure absolute paths
args.gem5dir = os.path.abspath(args.gem5dir)
args.checkpointdir = os.path.abspath(args.checkpointdir)
args.resultdir = os.path.abspath(args.resultdir)
args.specexedir = os.path.abspath(args.specexedir)

#Construct list of commands to be executed in parallel
commands = []
checkpoint_paths = glob.glob(args.checkpointdir + "/**/m5.cpt", recursive=True)

#Emit command for each checkpoint
for depshift in [0, 1, 2, 3, 4, 5, 6 ,7, 8, 9]:
    for checkpoint_path in checkpoint_paths:

        spec_name = checkpoint_path.split('/')[-5]
        spec_short_name = spec_name.split('.')[-1]
        spec_idx = int(checkpoint_path.split('/')[-4])
        checkpoint_idx = int(checkpoint_path.split('/')[-2].split('_')[1])

        checkpoint_dir ='/'.join(checkpoint_path.split('/')[:-2])
        result_dir = f"{args.resultdir}/{depshift}/{spec_name}/{spec_idx}/{checkpoint_idx}"

        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        trace_dir = f"{args.trace_dir}/{spec_name}/{spec_idx}/{checkpoint_idx}"
        if (args.gen_trace or args.refine_trace) and not os.path.exists(trace_dir):
            os.makedirs(trace_dir)

        spec_exe_path = f'{args.specexedir}/{spec_name}/{spec_short_name}_base.mytest-m64'
        spec_exe_dir = f'{args.specexedir}/{spec_name}'
        benchopts = ' '.join(workloads[spec_name].args[spec_idx])

        #Skip skip run if already complete
        if os.path.exists(result_dir + '/run.done'):
            with open(result_dir + '/run.done', 'r') as exitcode:
                if int(exitcode.read().strip()) == 0:
                    print(f'Skipped {result_dir} (run.done exists with 0 exit code)')
                    continue


        if workloads[spec_name].std_inputs is not None:
            benchinfile = workloads[spec_name].std_inputs[spec_idx]
        else:
            benchinfile = None

        command = []
        command.extend([f'{args.gem5dir}/build/X86/gem5' + ('.debug' if args.debug
                        else '.fast'), 
                        f'--outdir={result_dir}',

                        f'{args.gem5dir}/configs/deprecated/example/se.py',

                        #Checkpoint bs
                        '--restore-simpoint-checkpoint',
                        f'--checkpoint-restore={checkpoint_idx + 1}',
                        f'--checkpoint-dir={checkpoint_dir}',
                        '--restore-with-cpu=X86AtomicSimpleCPU',
                        
                        #Workload
                        f'--cmd={spec_exe_path}',
                        f'--options={benchopts}',
                        f'--mem-type=DDR3_1600_8x8',
                        f'--mem-size={args.memsize}GB',
                        f'--mem-channels={2}',

                        #Luke XL params
                        '--cpu-type=X86O3CPU',
                        '--caches',
                        '--l2cache',
                        '--l1d_size=256KiB',
                        '--l1i_size=256KiB',
                        '--l2_size=4MB',
                        f"--lsq-dep-check-shift={depshift}"
                        ])

        
        if benchinfile is not None:
            command.extend(['--input', benchinfile])

        commands.append((result_dir, spec_exe_dir, trace_dir, command))

#Function for single blocking program call
def run_command(command_tuple):
    result_dir, spec_exe_dir, trace_dir, command = command_tuple

    #Create modified environment if tracing enabled
    my_env = os.environ.copy()
    
    if (args.gen_trace):
        my_env["ORACLEMODE"] = "Trace"
    elif (args.refine_trace):
        my_env["ORACLEMODE"] = "Refine"
        
    if ((args.gen_trace) or (args.refine_trace)):
        my_env["TRACEDIR"] = trace_dir

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%d.%m %H:%M')

    print(f"{formatted_datetime}: Running {result_dir}")

    with open(result_dir + "/run.log", 'w+') as log:
        log.write(' '.join(command))
        process = subprocess.Popen(command, cwd=spec_exe_dir, stdout=log, stderr=log, env=my_env)
        (output, err) = process.communicate()  
        p_status = process.wait()

    with open(result_dir  + "/run.done", 'w+') as statusf:
        statusf.write(str(p_status))
    
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%d.%m %H:%M')
    print(f"{formatted_datetime}: Finished {result_dir} with exit code {p_status}")
        
#Execute commands in parallel with pool
pool = multiprocessing.Pool(args.jobs)

with pool:
    pool.map(run_command, commands)

print("Done")