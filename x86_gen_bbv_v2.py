import argparse
import m5
from m5.objects import *



parser = argparse.ArgumentParser(
                prog='Project Gem5 Config Script',
                description='Generate Basic Block Vectors for Simpoints clustering')

parser.add_argument('--workload',
                help='Path to workload',
                required=True)

parser.add_argument('--interval',
                type=int,
                default=10**7,
                help='Set simpoints inderval duration in instructions')

args = parser.parse_args()



system = System()

# Create a source clock for the system and set the clock period
system.clk_domain = SrcClockDomain(
    clock='1GHz',
    voltage_domain=VoltageDomain()
)

system.mem_mode = 'atomic'
system.mem_ranges = [AddrRange('8GB')]
system.membus = SystemXBar()

system.cpu = X86AtomicSimpleCPU()
system.cpu.addSimPointProbe(args.interval)
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports


system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports


system.workload = SEWorkload.init_compatible(args.workload)

process = Process()
process.cmd = [args.workload]
system.cpu.workload = process
system.cpu.createThreads()

root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation!")

exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

