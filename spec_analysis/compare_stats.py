import matplotlib.pyplot as plt
import numpy as np
import os
import glob

def aggregate_stat(res_dir, checkpoint_dir, statname):
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
                    #To read the actual warmed up stat only
                    break_val = 1
                    for line in lines:
                        if statname in line:
                            if break_val == 2:
                                linesplit = line.split(' ')
                                linesplitclean = [x for x in linesplit if x != '']
                                stat_value = float(linesplitclean[1])
                                break
                            else:
                                break_val += 1
                                continue

                if spec_benchmark in stat_dict:
                    stat_dict[spec_benchmark] += weight * stat_value
                else:
                    stat_dict[spec_benchmark] = weight * stat_value

    return stat_dict


baseline_dir = "/home/michal/Desktop/windows/FYP/spec_2017_rate_results"
new_dir  = "/home/michal/Desktop/windows/FYP/spec_2017_rate_results_r4"
checkpoint_dir = "/home/michal/Desktop/spec_2017_rate_checkpoints"

stat_name = "simTicks"

base_dict = aggregate_stat(
                baseline_dir,
               checkpoint_dir,
               stat_name
               )

new_dict  = aggregate_stat(
                new_dir,
               checkpoint_dir,
               stat_name
               )

labels = list(base_dict.keys())
labels.sort()

values = [(base_dict[key] - new_dict[key])/base_dict[key] * 100 for key in labels]

# Creating the bar graph
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16 

plt.figure(figsize=(14, 6))  # Set figure size
plt.bar(labels, values, color='blue', edgecolor='black')

# Adding labels and title
#plt.xlabel('Benchmarks')
plt.ylabel('IPC Improvement (%)')
#plt.title('Percentage Change from Base to New Values')

plt.xticks(rotation=90) 
plt.subplots_adjust(bottom=0.2) 

# Showing the plot
plt.tight_layout()
plt.savefig(f'trace_analysis/figures/perf_improvement.png', dpi=300)
plt.show(block=True)

# Oracle steps
base_dict = aggregate_stat(
                baseline_dir,
               checkpoint_dir,
               stat_name
               )
