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
new_dir  = "/home/michal/Desktop/windows/FYP/spec_2017_rate_results_r"
checkpoint_dir = "/home/michal/Desktop/spec_2017_rate_checkpoints"
barrier_dir = "/home/michal/Desktop/spec_2017_rate_barrier"

stat_name = "system.switch_cpus.smMemOrderViolations"
stat_name1 = "system.switch_cpus.smMDPOKBadPred"

dict = aggregate_stat(
                baseline_dir,
               checkpoint_dir,
               stat_name
               )
x1 = [sum(dict.values())/(23*10000)]

dict = aggregate_stat(
                baseline_dir,
               checkpoint_dir,
               stat_name1
               )
x2 = [sum(dict.values())/(23*10000)]

for i in range(1, 5):

    new_dict  = aggregate_stat(
                    new_dir+str(i),
                checkpoint_dir,
                stat_name
                )
    x1.append(sum(new_dict.values())/(23*10000))
    
    new_dict  = aggregate_stat(
                    new_dir+str(i),
                checkpoint_dir,
                stat_name1
                )
    x2.append(sum(new_dict.values())/(23*10000))

#Manually insert barrier run
    new_dict  = aggregate_stat(
                    new_dir+str(i),
                barrier_dir,
                stat_name
                )
    x1.append(sum(new_dict.values())/(23*10000))
    
    new_dict  = aggregate_stat(
                    new_dir+str(i),
                barrier_dir,
                stat_name1
                )
    x2.append(sum(new_dict.values())/(23*10000))


# Creating the bar graph
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16 


# Oracle steps

# Creating the index for each tick position
index = np.arange(len(x1))
labels = ["Store sets", "Oracle", "Refinement 1", "Refinement 2", "Refinement 3", "Barrier"]
# Creating bar for Product A
plt.figure(figsize=(14, 6))  # Set figure size

plt.bar(index, x1, bottom=x2,  label='Mem Order Violations', color='orange')

# Creating bar for Product B, stacked on top of Product A
plt.bar(index, x2, label='False dependencies', color='b')

# Adding labels and title
plt.xlabel('Trace collection stage')
plt.ylabel('Misses per kilo instruction')
plt.yscale('log')
plt.xticks(index, labels)
plt.ylim(0.01, 100)  # Adjust based on the expected range of your data


# Adding legend
plt.legend()

# Showing the plot
plt.tight_layout()
plt.savefig(f'oracle.png', dpi=300)
plt.show(block=True)
