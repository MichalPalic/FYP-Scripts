import argparse
from gem5.isas import ISA
from gem5.utils.requires import requires
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.boards.simple_board import SimpleBoard
from gem5.simulate.simulator import Simulator
from m5.objects import *
from project_workloads import suites, build_workload
from gem5.utils.simpoint import SimPoint
from pathlib import Path
from gem5.simulate.exit_event import ExitEvent
from gem5.simulate.exit_event_generators import simpoints_save_checkpoint_generator, save_checkpoint_generator 

def parse_args():
    parser = argparse.ArgumentParser(
                    prog='Project Gem5 Config Script',
                    description='Run ARM experiemnts')
    parser.add_argument('--exp',
                    help='Run premade experiemnt', required=True)
    parser.add_argument('--suite',
                    default='spec2006_train',
                    choices=suites.keys(),
                    help='Run premade experiemnt')
    parser.add_argument('--idx',
                    type=int,
                    default=0,
                    help='Pick bench index')
    
    parser.add_argument('--restore-checkpoint',
                    type=str,
                    default=None,
                    help='Start simulation from checkpoint')
    
    parser.add_argument(
        "--simpoint-interval",
        type=int,
        required=True,
        help="Intervals at which the simpoints were taken"
    )
    
    parser.add_argument(
        "--warmup-interval",
        type=int,
        required=True,
        help="Simulation warmup interval"
    )
    
    parser.add_argument(
        "--simpoint-file",
        type=str,
        required=True,
        help="Path to file containing simpoints"
    )
    
    parser.add_argument(
        "--weight-file",
        type=str,
        required=True,
        help="Path to file containing simpoint weights"
    )
    
    parser.add_argument(
        "--checkpoint-path",
        type=str,
        required=True,
        help="Path to the folder where the checkpoints will be saved"
    )
    
    return parser.parse_args() 

requires(isa_required=ISA.X86)

args = parse_args()

cache_hierarchy = NoCache()
 
memory = SingleChannelDDR3_1600(size="8GB")

processor = SimpleProcessor(cpu_type=CPUTypes.ATOMIC, isa=ISA.X86, num_cores=1)

board = SimpleBoard(
    clk_freq="1GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

simpoint = SimPoint(
    simpoint_interval=args.simpoint_interval,
    simpoint_file_path=args.simpoint_file,
    weight_file_path=args.weight_file,
    warmup_interval=args.warmup_interval
)

checkpoint = None
if args.restore_checkpoint is not None:
    checkpoint = Path(args.restore_checkpoint)

# board.set_workload(workload_factory(args.exp, args.idx, simpoint))
board.set_workload(build_workload(suites[args.suite], args.exp, args.idx, simpoint, checkpoint))

checkpoint_dir = Path(args.checkpoint_path)
checkpoint_dir.mkdir(exist_ok=True)

simulator = Simulator(
    board=board, 
    on_exit_event={ ExitEvent.SIMPOINT_BEGIN: simpoints_save_checkpoint_generator(checkpoint_dir, simpoint) }
    #on_exit_event={ ExitEvent.MAX_TICK: save_checkpoint_generator() }
)
simulator.run()

print(
    "Exiting @ tick {} because {}.".format(
        simulator.get_current_tick(), simulator.get_last_exit_event_cause()
    )
)
