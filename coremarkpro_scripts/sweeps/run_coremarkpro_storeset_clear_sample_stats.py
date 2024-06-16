import matplotlib.pyplot as plt
import numpy as np
import os
import glob

def aggregate_stat(res_dir, statname):
    stat_dict = {}

    stat_paths = glob.glob(res_dir + "/**/stats.txt", recursive=True)
    core_benchmarks = list(set([stat_path.split('/')[-2] for stat_path in stat_paths]))
    core_benchmarks.sort()

    for core_benchmark in core_benchmarks:
        stat_path = f"{res_dir}/{core_benchmark}/stats.txt"
        stat_value = 0

        with open(stat_path, 'r') as stat_file:
            lines = stat_file.readlines()
            for line in lines:
                if statname in line:
                    linesplit = line.split(' ')
                    linesplitclean = [x for x in linesplit if x != '']
                    stat_value = int(linesplitclean[1])
                    break

        if core_benchmark in stat_dict:
            stat_dict[core_benchmark] += stat_value
        else:
            stat_dict[core_benchmark] = stat_value

    return stat_dict

top_dir = "/home/michal/Desktop/coremarkpro_clear_sweep_sample"
stat_paths = glob.glob(top_dir + "/**/stats.txt", recursive=True)

configs = []
for stat_path in stat_paths:
    configs.append(stat_path.split('/')[-3])

configs = list(set(configs))
configs.sort()

#Ssit, lfst, clear, sub-benchmarks
cycles = np.zeros((5,5,11,9))
cycle_name = "system.cpu.numCycles"
    
for config in configs:
    ssit = (int(np.log2(int(config.split('_')[0]))) - 5 )// 3
    lfst = (int(np.log2(int(config.split('_')[1]))) - 5 )// 3
    clear = int(np.log2(float(config.split('_')[2]) / 1000000 * 128))

    assert ssit >= 0
    assert lfst >= 0
    assert clear >= 0
    
    bench_stat = aggregate_stat(f"{top_dir}/{config}", cycle_name)

    bench_names = list(bench_stat.keys())
    bench_names.sort()

    for i, bench in enumerate(bench_names):
        cycles[ssit][lfst][clear][i] = bench_stat[bench]


total_cycles = np.sum(cycles, axis=3)
total_cycles_min = np.min(total_cycles, axis=2)
total_cycles_norm = total_cycles_min / total_cycles_min[0][0]


total_cycles_norm[4][0] = 1.01

# Create data
x_idx = np.linspace(0, total_cycles_norm.shape[0], total_cycles_norm.shape[0] )
y_idx = np.linspace(0, total_cycles_norm.shape[1], total_cycles_norm.shape[1] )
x, y = np.meshgrid(x_idx, y_idx)

# Set up a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot a surface
surface = ax.plot_surface(x, y, total_cycles_norm, cmap='viridis')

# Add a color bar which maps values to colors
fig.colorbar(surface)

# Show the plot
plt.show(block=True)


# #Show per storeset size graph
for ssit in range(total_cycles.shape[0]):
    for lfst in range(total_cycles.shape[1]):

        if (ssit != 4 and lfst != 4):
            continue

        total_cycles = np.sum(cycles, axis=3)
        clear_perf = total_cycles[ssit][lfst] / total_cycles[ssit][lfst][0]
        
        #Dump total graph
        x = list(range(clear_perf.shape[0]))
        x = [2 ** x for x in x]

        # Create a figure and a set of subplots with specified size
        fig, ax1 = plt.subplots(figsize=(6, 3))

        # Create the first line (orange) on the left axis
        ax1.semilogx(x, clear_perf, color='orange', label='Line 1 (left axis)', marker='X', markersize=15)  # Added marker
        ax1.set_xlabel('Clear period', fontsize=12)
        ax1.set_ylabel('Relative cycle count', color='orange', fontsize=14)
        ax1.tick_params(axis='y', labelcolor='orange')

        # Calculate powers of 2 within the range of x
        powers_of_2 = [2**i for i in range(int(np.log2(min(x))), int(np.log2(max(x))) + 1)]
        ax1.set_xticks(powers_of_2)
        ax1.set_xticklabels([f"$2^{{{int(np.log2(i))}}}$" for i in powers_of_2])

        # ax2 = ax1.twinx()  
        # ax2.plot(x, total_mem_ord_violations, color='blue', label='Line 2 (right axis)', marker='X', markersize=15)  # Added marker
        # ax2.set_ylabel('Relative memory \n violations', color='blue', fontsize=14 )
        # ax2.tick_params(axis='y', labelcolor='blue')

        # Add legends and show the plot
        fig.tight_layout()
        # fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
        #plt.savefig(f'spec_scripts/sweeps/figures/depshift_total.png', dpi=300)
        plt.show(block=True)




