import matplotlib.pyplot as plt
import numpy as np
import os
import glob

def aggregate_stat(res_dir, checkpoint_dir, statname, occurence):
    stat_dict = {}
    weight_paths = glob.glob(checkpoint_dir + "/**/simpoints.weights", recursive=True)
    weight_paths.sort()

    spec_benchmarks = list(set([weight_path.split('/')[-3] for weight_path in weight_paths]))
    spec_benchmarks.sort()

    for spec_benchmark in spec_benchmarks:

        for weight_path in weight_paths:

            if spec_benchmark not in weight_path:
                continue

            #Parse weight path
            weight_path_split = weight_path.split('/')
            benchmark_idx = weight_path_split[-2]

            #Parse out simpoints
            weights = []
            with open(weight_path, 'r') as w:
                w_lines = w.readlines()
                for line in w_lines:
                    weights.append( float(line.split(' ')[0]))
            
            for idx, weight in enumerate(weights):
                stat_path = f"{res_dir}/{spec_benchmark}/{benchmark_idx}/{idx}/stats.txt"
                stat_value = 0

                if not os.path.isfile(stat_path):
                    continue

                with open(stat_path, 'r') as stat_file:
                    lines = stat_file.readlines()
                    n = 1
                    for line in lines:
                        
                        if statname in line:
                            if n == occurence:
                                linesplit = line.split(' ')
                                linesplitclean = [x for x in linesplit if x != '']
                                stat_value = float(linesplitclean[1])
                                break
                            else:
                                n += 1

                if spec_benchmark in stat_dict:
                    stat_dict[spec_benchmark] += weight * stat_value
                else:
                    stat_dict[spec_benchmark] = weight * stat_value

    return stat_dict


checkpoint_dir = "/home/michal/Desktop/spec_2017_rate_checkpoints"
top_dir = "/home/michal/Desktop/spec_2017_rate_sweep_branches_deepjseng"
stat_paths = glob.glob(top_dir + "/**/stats.txt", recursive=True)

configs = []
for stat_path in stat_paths:
    configs.append(stat_path.split('/')[-5])

configs = list(set(configs))
configs.sort()

branches = [0, 1, 2, 4, 8]
clear_mult = [0.003906, 0.015625, 0.0625, 0.25, 1]
arr_dim = (len(branches),len(clear_mult),1)

#Ssit, lfst, clear, sub-benchmarks
# cold_miss = np.zeros(arr_dim)
# cold_miss_name = "system.cpu.smMDPMispredictionsCold"

# false_dep = np.zeros(arr_dim)
# false_dep_name = "system.cpu.smMDPOKBadPred"

cycles = np.zeros(arr_dim)
cycle_name = "system.switch_cpus.numCycles"
    
for config in configs:
    branch_idx = branches.index(int(config.split('_')[0]))
    clear_mult_idx = clear_mult.index(float(config.split('_')[1]))

    #Aggregate cycles
    bench_stat = aggregate_stat(f"{top_dir}/{config}", checkpoint_dir, cycle_name, 2)

    bench_names = list(bench_stat.keys())
    bench_names.sort()

    for i, bench in enumerate(bench_names):
        cycles[branch_idx][clear_mult_idx][i] = bench_stat[bench]
    
    # #Aggregate cold misses
    # bench_stat = aggregate_stat(f"{top_dir}/{config}", cold_miss_name)

    # bench_names = list(bench_stat.keys())
    # bench_names.sort()

    # for i, bench in enumerate(bench_names):
    #     cold_miss[ssit][lfst][clear][i] = bench_stat[bench]
    
    # #Aggregate false deps
    # bench_stat = aggregate_stat(f"{top_dir}/{config}", false_dep_name)

    # bench_names = list(bench_stat.keys())
    # bench_names.sort()

    # for i, bench in enumerate(bench_names):
    #     false_dep[ssit][lfst][clear][i] = bench_stat[bench]


total_cycles = np.sum(cycles, axis=2)
total_cycles_norm = total_cycles / total_cycles[0][0]

total_cycles_norm[0][4] = 1


# Create data
x_idx = np.linspace(0, total_cycles_norm.shape[0], total_cycles_norm.shape[0] )
y_idx = np.linspace(0, total_cycles_norm.shape[1], total_cycles_norm.shape[1] )
x, y = np.meshgrid(x_idx, y_idx)

# Set up a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot a surface
surface = ax.plot_surface(x, y, total_cycles_norm, cmap='viridis')
ax.set_xlabel('Branches')
ax.set_ylabel('Clear period')
ax.set_zlabel('CPI')

# Show the plot
plt.show(block=True)


# #Show per storeset size graph
for branch_idx in range(total_cycles.shape[0]):

    total_cycles = np.sum(cycles, axis=2)
    clear_perf = total_cycles[branch_idx] / total_cycles[branch_idx][0]

    # Create a figure and a set of subplots with specified size
    fig, ax1 = plt.subplots(figsize=(6, 3))

    # Create the first line (orange) on the left axis
    ax1.plot(branches, clear_perf, color='orange', label='Line 1 (left axis)', marker='X', markersize=15)  # Added marker
    ax1.set_xlabel('Clear period', fontsize=12)
    ax1.set_ylabel('Relative cycle count', color='orange', fontsize=14)
    ax1.tick_params(axis='y', labelcolor='orange')

    ax1.set_xticks(list(range(len(branches))))
    ax1.set_xticklabels(branches)

    # ax2 = ax1.twinx()  
    # ax2.plot(x, total_mem_ord_violations, color='blue', label='Line 2 (right axis)', marker='X', markersize=15)  # Added marker
    # ax2.set_ylabel('Relative memory \n violations', color='blue', fontsize=14 )
    # ax2.tick_params(axis='y', labelcolor='blue')

    # Add legends and show the plot
    fig.tight_layout()
    # fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
    plt.savefig(f'spec_scripts/sweeps/figures_branches/spec_{branches[branch_idx]}.png', dpi=300)
    #plt.show(block=True)
    plt.close()


    # #Dependence graphs

    # total_cold_miss = np.sum(cold_miss, axis=3)[ssit][lfst]
    # total_false_dep = np.sum(false_dep, axis=3)[ssit][lfst]

    # #Dump total graph
    # x = [0.000488, 0.000976, 0.001953, 0.003906, 0.007812, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8]
    # x = [ x_itm * 1000000 for x_itm in x]

    # # Create a figure and a set of subplots with specified size
    # fig, ax1 = plt.subplots(figsize=(6, 3))

    # # Create the first line (orange) on the left axis
    # ax1.semilogx(x, total_cold_miss, color='orange', label='Total cold misses', marker='X', markersize=15)  # Added marker
    # ax1.set_xlabel('Clear period', fontsize=12)
    # ax1.set_ylabel('Relative cycle count', color='orange', fontsize=14)
    # ax1.tick_params(axis='y', labelcolor='orange')

    # # Calculate powers of 2 within the range of x
    # powers_of_2 = [2**i for i in range(int(np.log2(min(x))), int(np.log2(max(x))) + 1)]
    # ax1.set_xticks(powers_of_2)
    # ax1.set_xticklabels([f"$2^{{{int(np.log2(i))}}}$" for i in powers_of_2])

    # ax2 = ax1.twinx()  
    # ax2.plot(x, total_false_dep, color='blue', label='Total false dependencies', marker='X', markersize=15)  # Added marker
    # ax2.set_ylabel('Relative memory \n violations', color='blue', fontsize=14 )
    # ax2.tick_params(axis='y', labelcolor='blue')

    # # Add legends and show the plot
    # fig.tight_layout()
    # fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
    # plt.savefig(f'coremarkpro_scripts/sweeps/figures/core_deps_{ssit}_{lfst}.png', dpi=300)
    # #plt.show(block=True)
    # plt.close()




