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


result_dir = "/home/michal/Desktop/spec_2017_rate_sweep_depshift"
checkpoint_dir = "/home/michal/Desktop/spec_2017_rate_checkpoints"


numCycles = []
mem_ord_violations = []

total_cycles =[]
total_mem_ord_violations = []

for i in range(9):
    numCycles.append(aggregate_stat(
                    f"{result_dir}/{i}" ,
                    checkpoint_dir,
                    "system.switch_cpus.ipc", 2))
    
    mem_ord_violations.append(aggregate_stat(
                    f"{result_dir}/{i}" ,
                    checkpoint_dir,
                    "system.switch_cpus.smMemOrderViolations", 2))
    
    #Aggregate across all benchmarks
    sum_num_cycles = 0
    sum_mem_ord_violations = 0
    
    for benchmark in list(numCycles[-1].keys()):
        sum_num_cycles += numCycles[-1][benchmark]
        sum_mem_ord_violations += mem_ord_violations[-1][benchmark]

    total_cycles.append(sum_num_cycles)
    total_mem_ord_violations.append(sum_mem_ord_violations)

#Normalise total metrics
ref_cycles = total_cycles[0]
ref_mem_ord_violations = total_mem_ord_violations[0]

total_cycles = [x / float(ref_cycles) for x in total_cycles]
total_mem_ord_violations = [x / float(ref_mem_ord_violations) for x in total_mem_ord_violations]

out = ""
for perf in total_cycles:
    out += ' & ' + str('%.2f' % ((perf-1)* 100))
print(f"Total {out} \\\\")

#Dump total graph
x = list(range(9))
x = [2 ** x for x in x]

# Create a figure and a set of subplots with specified size
fig, ax1 = plt.subplots(figsize=(6, 3))

# Create the first line (orange) on the left axis
ax1.semilogx(x, total_cycles, color='orange', label='Line 1 (left axis)', marker='X', markersize=15)  # Added marker
ax1.set_xlabel('Memory dependence check granularity [bytes]', fontsize=12)
ax1.set_ylabel('Instructions per clock', color='orange', fontsize=14)
ax1.tick_params(axis='y', labelcolor='orange')

# Calculate powers of 2 within the range of x
powers_of_2 = [2**i for i in range(int(np.log2(min(x))), int(np.log2(max(x))) + 1)]
ax1.set_xticks(powers_of_2)
ax1.set_xticklabels([f"$2^{{{int(np.log2(i))}}}$" for i in powers_of_2])

ax2 = ax1.twinx()  
ax2.plot(x, total_mem_ord_violations, color='blue', label='Line 2 (right axis)', marker='X', markersize=15)  # Added marker
ax2.set_ylabel('Memory \n violation count', color='blue', fontsize=14 )
ax2.tick_params(axis='y', labelcolor='blue')

# Add legends and show the plot
fig.tight_layout()
# fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
plt.savefig(f'spec_scripts/sweeps/figures/depshift_total.png', dpi=300)
#plt.show(block=True)

y1_tot = [0,0,0,0,0,0,0,0,0]
for benchmark in list(numCycles[0].keys()):
    x = list(range(9))
    x = [2 ** x for x in x]
    y1 = []
    y2 = []
    
    for i, dict in enumerate(numCycles):
        y1.append(numCycles[i][benchmark]/numCycles[0][benchmark])
        y2.append(mem_ord_violations[i][benchmark]/mem_ord_violations[0][benchmark])
        
    out = ""
    for i, perf in enumerate(y1):
        out += ' & ' + str('%.2f' % ((perf-1)* 100))
        y1_tot[i] +=((perf-1)* 100)
    print(f"{benchmark} {out} \\\\")
    # Create a figure and a set of subplots with specified size
    fig, ax1 = plt.subplots(figsize=(6, 3))

    # Create the first line (orange) on the left axis
    ax1.semilogx(x, y1, color='orange', label='Line 1 (left axis)', marker='X', markersize=15)  # Added marker
    ax1.set_xlabel('Memory dependence check granularity [bytes]', fontsize=12)
    ax1.set_ylabel('Instructions per clock', color='orange', fontsize=14)
    ax1.tick_params(axis='y', labelcolor='orange')

    # Calculate powers of 2 within the range of x
    powers_of_2 = [2**i for i in range(int(np.log2(min(x))), int(np.log2(max(x))) + 1)]
    ax1.set_xticks(powers_of_2)
    ax1.set_xticklabels([f"$2^{{{int(np.log2(i))}}}$" for i in powers_of_2])

    ax2 = ax1.twinx()  
    ax2.plot(x, y2, color='blue', label='Line 2 (right axis)', marker='X', markersize=15)  # Added marker
    ax2.set_ylabel('Memory \n violation count', color='blue', fontsize=14 )
    ax2.tick_params(axis='y', labelcolor='blue')

    # Add legends and show the plot
    fig.tight_layout()
    # fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.9))
    plt.savefig(f'spec_scripts/sweeps/figures/depshift_{benchmark}.png', dpi=300)
    plt.close()
    #plt.show(block=False)

print([y/23 for y in y1_tot])