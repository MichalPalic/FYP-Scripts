import argparse
import os
from workloads import *
import multiprocessing
import subprocess


parser = argparse.ArgumentParser(
                prog='Valgrind BBV Config Script',
                description='Generate Basic Block Vectors for Simpoints clustering')

parser.add_argument('--interval',
                type=int,
                default=10**7,
                help='Set simpoints interval duration in instructions')

parser.add_argument('--minispec',
                type=str,
                default="/home/michal/Desktop/MINISPEC2017",
                help='Path to compiled "Mini"SPEC (Extracted executables and input files)')

parser.add_argument('--outpath',
                type=str,
                default="/home/michal/Desktop/SPEC2017_BBV",
                help='Output path for saving bbvectors')

args = parser.parse_args()


if not os.path.exists(args.minispec):
    print("Minispec path does not exist")
    exit

if not os.path.isdir(args.minispec):
    print("Minispec not a directory")
    exit

entries = os.listdir(args.minispec)
folders = [folder for folder in entries if os.path.isdir(args.minispec+ '/' + folder)]

commands = []

for folder in folders:
    benchmark = workloads[folder]
    for idx, benchmark_args in enumerate(benchmark.args):
        command = []

        #Create missing files and directories 
        outdir = args.outpath + '/' + folder + f'/{idx}'

        if not os.path.exists(outdir):
            os.makedirs(outdir)


        logdir = args.outpath + '/' + folder + f'/{idx}'
        logpath = logdir + '/bb.log'

        if not os.path.exists(logdir):
            os.makedirs(logdir)

        with open(logpath, 'w') as out_file:
                out_file.write('')
    
        programname = folder.split('.')[1]
        programdir = args.minispec + '/' + folder
        programpath = programname + '_base.mytest-m64'

        assert os.path.isfile(programdir + '/' + programpath), f"Failed to infer executable path: {programpath}"

        # instr = ''
        # if benchmark.std_inputs is not None:
        #     instr = f' < {benchmark.std_inputs[idx]}'

        command.extend(['valgrind',  '--tool=exp-bbv', '--interval-size=10000000',
                        f'--bb-out-file=bb_{idx}.txt', f'./{programpath}' ])
        command.extend(benchmark_args)

        commands.append((programdir, logpath, idx, command))
        
def run_command(command_tuple):
    programdir, logpath, idx, command = command_tuple
    os.chdir(programdir)
    with open(logpath, 'w+') as log:
        process = subprocess.Popen(command, stdout=log) #
        (output, err) = process.communicate()  
        p_status = process.wait()

        
#Execute commands in parallel
MAX_THREADS = 1
pool = multiprocessing.Pool(MAX_THREADS)

with pool:
    pool.map(run_command, commands)




print("Got here")
