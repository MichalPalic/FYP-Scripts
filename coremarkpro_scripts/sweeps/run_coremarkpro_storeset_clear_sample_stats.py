import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from matplotlib.ticker import FormatStrFormatter

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
                    stat_value = float(linesplitclean[1])
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
cold_miss = np.zeros((5,5,15,9))
cold_miss_name = "system.cpu.smMDPMispredictionsCold"

false_dep = np.zeros((5,5,15,9))
false_dep_name = "system.cpu.smMDPOKBadPred"

cycles = np.zeros((5,5,15,9))
cycle_name = "system.cpu.ipc"

cycles_count = np.zeros((5,5,15,9))
cycle_count_name = "system.cpu.numCycles"



# Set global font sizes
plt.rcParams['axes.labelsize'] = 12 
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10 
    
for config in configs:
    ssit = (int(np.log2(int(config.split('_')[0]))) - 5 )// 3
    lfst = (int(np.log2(int(config.split('_')[1]))) - 5 )// 3
    clear = round(np.log2(float(config.split('_')[2]) / 1000000)) + 11

    assert ssit >= 0
    assert lfst >= 0
    assert clear >= 0

    #Aggregate cycles
    bench_stat = aggregate_stat(f"{top_dir}/{config}", cycle_name)

    bench_names = list(bench_stat.keys())
    bench_names.sort()

    for i, bench in enumerate(bench_names):
        cycles[ssit][lfst][clear][i] = bench_stat[bench]
    
    #Aggregate cold misses
    bench_stat = aggregate_stat(f"{top_dir}/{config}", cold_miss_name)

    bench_names = list(bench_stat.keys())
    bench_names.sort()

    for i, bench in enumerate(bench_names):
        cold_miss[ssit][lfst][clear][i] = bench_stat[bench]
    
    #Aggregate false deps
    bench_stat = aggregate_stat(f"{top_dir}/{config}", false_dep_name)

    bench_names = list(bench_stat.keys())
    bench_names.sort()

    for i, bench in enumerate(bench_names):
        false_dep[ssit][lfst][clear][i] = bench_stat[bench]

    #Cycles count name
    bench_stat = aggregate_stat(f"{top_dir}/{config}", cycle_count_name)

    bench_names = list(bench_stat.keys())
    bench_names.sort()

    for i, bench in enumerate(bench_names):
        cycles_count[ssit][lfst][clear][i] = bench_stat[bench]


total_cycles = np.mean(cycles, axis=3)
total_cycles_norm  = np.max(total_cycles, axis=2)


# Create data
x_idx = np.linspace(0, total_cycles_norm.shape[0], total_cycles_norm.shape[0] )
y_idx = np.linspace(0, total_cycles_norm.shape[1], total_cycles_norm.shape[1] )
x, y = np.meshgrid(x_idx, y_idx)

# Set up a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot a surface
surface = ax.plot_surface(x, y, total_cycles_norm, cmap='viridis')
ax.set_xticks(list(range(5)), list(reversed([64, 512, 4096, 32768, 262144])))
ax.set_xlabel("LFST size", labelpad=10)
ax.set_yticks(list(range(5)), [64, 512, 4096, 32768, 262144])
ax.set_ylabel("SSIT size", labelpad=10)
ax.set_zlabel("average IPC", labelpad=10)
ax.set_zticks([1.64, 1.65, 1.66, 1.67])
ax.zaxis.set_major_formatter(FormatStrFormatter('%.2f'))

# Show the plot
#plt.show(block=True)
np.savetxt("surface.csv", (total_cycles_norm/total_cycles_norm[0][0] - 1)*100, delimiter=",", fmt='%.2f')
np.savetxt("surface2.csv", (total_cycles_norm), delimiter=",", fmt='%.4f')
#Do least squares
total_cycles = np.sum(cycles_count, axis=3)
total_cycles_f = total_cycles.flatten()
total_cold_miss = np.sum(cold_miss, axis=3)
total_cold_miss_f = total_cold_miss.flatten()
total_false_dep  =np.sum(false_dep, axis=3)
total_false_dep_f = total_false_dep.flatten()
total_const = np.ones_like(total_false_dep_f)

a = np.stack((total_cold_miss_f, total_false_dep_f, total_const), axis=1)
coefficients = np.linalg.lstsq(a, total_cycles_f)

print(f"Coeffs: {coefficients[0]}")
bench_inst_counts = [35180535, 4825408184, 61263990, 908054065, 900156502, 86898627, 16155604, 70113884, 2125785949]
pred_cycles = np.sum(cold_miss, axis=3)* coefficients[0][0] + np.sum(false_dep, axis=3) * coefficients[0][1] + coefficients[0][2]
pred_ipc = sum(bench_inst_counts) / pred_cycles
# exit()

# #Show per storeset size graph
for ssit in range(total_cycles.shape[0]):
    for lfst in range(total_cycles.shape[1]):
        
        total_cycles = np.mean(cycles, axis=3)
        clear_perf = total_cycles[ssit][lfst]

        clear_pred_perf = pred_ipc[ssit][lfst]
        
        #Dump total graph
        x = [0.000488, 0.000976, 0.001953, 0.003906, 0.007812, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8]
        x = [ x_itm * 1000000 for x_itm in x]

        # Create a figure and a set of subplots with specified size
        fig, ax1 = plt.subplots(figsize=(6, 3))

        # Create the first line (orange) on the left axis
        ax1.semilogx(x, clear_perf, color='orange', label='Real IPC', marker='X', markersize=15)  # Added marker
        ax1.set_xlabel('Clear period', fontsize=12)
        ax1.set_ylabel('Average IPC', color='blue', fontsize=14)
        ax1.tick_params(axis='y', labelcolor='orange')

        # Calculate powers of 2 within the range of x
        powers_of_2 = [2**i for i in range(int(np.log2(min(x))), int(np.log2(max(x))) + 1)]
        ax1.set_xticks(powers_of_2)
        ax1.set_xticklabels([f"$2^{{{int(np.log2(i))}}}$" for i in powers_of_2])

        # ax2 = ax1.twinx()  
        ax1.plot(x, clear_pred_perf, color='blue', label='Predicted IPC', marker='X', markersize=15)  # Added marker
        #ax1.set_ylabel('Relative memory \n violations', color='blue', fontsize=14 )
        ax1.tick_params(axis='y', labelcolor='blue')

        # Add legends and show the plot
        fig.tight_layout()
        fig.legend(loc='lower center', bbox_to_anchor=(0.5, 0.25))
        plt.savefig(f'coremarkpro_scripts/sweeps/figures/core_clear_{ssit}_{lfst}.png', dpi=300)
        #plt.show(block=True)
        plt.close()


        #Dependence graphs

        total_cold_miss = np.sum(cold_miss, axis=3)[ssit][lfst]
        total_false_dep = np.sum(false_dep, axis=3)[ssit][lfst]

        #Dump total graph
        x = [0.000488, 0.000976, 0.001953, 0.003906, 0.007812, 0.015625, 0.03125, 0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8]
        x = [ x_itm * 1000000 for x_itm in x]

        # Create a figure and a set of subplots with specified size
        fig, ax1 = plt.subplots(figsize=(6, 3))

        # Create the first line (orange) on the left axis
        ax1.semilogx(x, total_cold_miss, color='orange', label='Total cold misses', marker='X', markersize=15)  # Added marker
        ax1.set_xlabel('Clear period', fontsize=12)
        ax1.set_ylabel('Cold mispredictions', color='orange', fontsize=14)
        ax1.tick_params(axis='y', labelcolor='orange')

        # Calculate powers of 2 within the range of x
        powers_of_2 = [2**i for i in range(int(np.log2(min(x))), int(np.log2(max(x))) + 1)]
        ax1.set_xticks(powers_of_2)
        ax1.set_xticklabels([f"$2^{{{int(np.log2(i))}}}$" for i in powers_of_2])

        ax2 = ax1.twinx()  
        ax2.plot(x, total_false_dep, color='blue', label='Total false dependencies', marker='X', markersize=15)  # Added marker
        ax2.set_ylabel('False dependence mispredictions', color='blue', fontsize=10 )
        ax2.tick_params(axis='y', labelcolor='blue')

        # Add legends and show the plot
        fig.tight_layout()
        #fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
        plt.savefig(f'coremarkpro_scripts/sweeps/figures/core_deps_{ssit}_{lfst}.png', dpi=300)
        #plt.show(block=True)
        plt.close()




