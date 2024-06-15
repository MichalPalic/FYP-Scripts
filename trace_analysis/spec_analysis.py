import sys
import matplotlib.pyplot as plt
import numpy as np
import ctypes
import os
import glob
import shelve
from matplotlib.ticker import MaxNLocator


cpplibrary = ctypes.CDLL("/home/michal/Desktop/fyp_scripts/trace_analysis/analysislib.so")

calculate_statistics = cpplibrary.calculate_statistics
calculate_statistics.argtypes = [ctypes.c_char_p, ctypes.c_float, ctypes.c_uint64]

get_seq_dists = cpplibrary.get_seq_dists
get_seq_dists.restype = ctypes.POINTER(ctypes.c_char_p)

get_eff_seq_dists = cpplibrary.get_eff_seq_dists
get_eff_seq_dists.restype = ctypes.POINTER(ctypes.c_char_p)

get_eff_seq_dists = cpplibrary.get_eff_seq_dists
get_eff_seq_dists.restype = ctypes.POINTER(ctypes.c_char_p)

get_branch_dists = cpplibrary.get_branch_dists
get_branch_dists.restype = ctypes.POINTER(ctypes.c_char_p)

get_takenness = cpplibrary.get_takenness
get_takenness.restype = ctypes.POINTER(ctypes.c_char_p)

get_path_counts = cpplibrary.get_path_counts
get_path_counts.restype = ctypes.POINTER(ctypes.c_char_p)

clear_all = cpplibrary.clear_all
clear_caches = cpplibrary.clear_caches

#Control parameters
fig_block = False
fig_h = 4
fig_w = 14
max_val = 1025
tick_space = 256
tick_space_hist = 5
log_scale = False

checkpoint_dir = "/home/michal/Desktop/spec_2017_rate_checkpoints"
trace_dir = "/home/michal/Desktop/windows/FYP/spec_2017_rate_trace"
result_dir = "/home/michal/Desktop/windows/FYP/spec_2017_rate_results"

weight_paths = glob.glob(checkpoint_dir + "/**/simpoints.weights", recursive=True)
weight_paths.sort()

#Aggregate stats
eff_seq_dists_p_aggregate = None
eff_seq_dists_p_aggregate_sum = 0
seq_dists_p_aggregate = None
seq_dists_p_aggregate_sum = 0
branch_dists_p_aggregate = None
branch_dists_p_aggregate_sum = 0
hist_p_aggregate = None
hist_p_aggregate_sum = 0
path_p_aggregate = None
path_p_aggregate_sum = 0

spec_benchmarks = list(set([weight_path.split('/')[-3] for weight_path in weight_paths]))
spec_benchmarks.sort()
spec_benchmarks = reversed(spec_benchmarks)

for bench_idx, spec_benchmark in enumerate(spec_benchmarks):
    #Completely reset backend state between benchmarks
    clear_all()

    # if bench_idx != 5:
    #     continue

    for weight_path in weight_paths:

        #Skip if doesn't belong
        if spec_benchmark not in weight_path:
            continue

        #Parse weight path
        weight_path_split = weight_path.split('/')
        benchmark_idx = weight_path_split[-2]
        benchmark_name = weight_path_split[-3]

        #Parse out simpoints
        weights = []
        with open(weight_path, 'r') as w:
            w_lines = w.readlines()
            for line in w_lines:
                weights.append( float(line.split(' ')[0]))

        for checkpoint_idx, weight in enumerate(weights):

            # if checkpoint_idx >= 1:
            #     break

            #Break backend dependencies between checkpoints
            clear_caches()

            trace_path = f"{trace_dir}/{benchmark_name}/{benchmark_idx}/{checkpoint_idx}/full_trace.csv.zst"

            # if not os.path.isfile(trace_path):
            #     continue

            print(f"Aggregating statistics for: {trace_path} with weight {weight}")
            calculate_statistics(trace_path.encode(encoding="ascii",errors="ignore"), float(weight), 1000000)

    print(f"Dumping graphs for: {spec_benchmark}")

    #Plot eff seq number dists
    pystr = ctypes.c_char_p.from_buffer(get_eff_seq_dists()).value.decode('utf-8')
    temp = pystr.split(',')[:-1]
    eff_seq_dists = [int(x.split(':')[0]) for x in temp]
    eff_seq_dists_counts = [float(x.split(':')[1]) for x in temp]
    eff_seq_dists_sum = sum(eff_seq_dists_counts)
    eff_seq_dists_p = [float(x)/eff_seq_dists_sum for x in eff_seq_dists_counts]

    frequencies = [0 for  i in range(max_val)]
    for idx, dist in enumerate(eff_seq_dists[1:max_val+1]):
        if dist < max_val + 1:
            frequencies[dist-1] = eff_seq_dists_p[idx]

    eff_seq_dists_p__cdf = [f"{i}:{sum(frequencies[:i])}" for i, x in enumerate(frequencies)]

    with open("Stat.txt", "a+") as myfile:
        myfile.write(f"{benchmark_name} effseqnum CDF: {eff_seq_dists_p__cdf} \n")

    #Aggregate for overall stats
    if eff_seq_dists_p_aggregate is None:
        eff_seq_dists_p_aggregate = [ x * eff_seq_dists_sum for x in frequencies ]
    else:
        eff_seq_dists_p_aggregate = [x + frequencies[i]*eff_seq_dists_sum for i,x in enumerate(eff_seq_dists_p_aggregate)]
    eff_seq_dists_p_aggregate_sum += eff_seq_dists_sum

    labels = [str(i) for i in range(0, max_val)]
    positions = np.arange(max_val)

    plt.figure(figsize=(fig_w, fig_h))
    plt.bar(positions, frequencies, color='blue', edgecolor='black')
    plt.xlabel('Linear sequence number distance')
    plt.ylabel('Normalised frequency')
    plt.xticks(positions[::tick_space], labels[::tick_space])
    if log_scale:
        plt.yscale('log')

    try:
        plt.savefig(f'trace_analysis/figures1024/{spec_benchmark}_eff_seq_dist.png', dpi=300)
    except:
        plt.show(block=fig_block)
        print("Failed to open figure path")
    
    #Plot branch dists
    pystr = ctypes.c_char_p.from_buffer(get_branch_dists()).value.decode('utf-8')
    temp = pystr.split(',')[:-1]
    branch_dists = [int(x.split(':')[0]) for x in temp]
    branch_dists_counts = [float(x.split(':')[1]) for x in temp]
    branch_dists_sum = sum(branch_dists_counts)
    branch_dists_p = [float(x)/branch_dists_sum for x in branch_dists_counts]

    frequencies = [0 for  i in range(max_val)]
    for idx, dist in enumerate(branch_dists[:max_val]):
        if dist < max_val:
            frequencies[dist] = branch_dists_p[idx]

    branch_dists_cdf = [f"{i}:{sum(frequencies[:i])}" for i, x in enumerate(frequencies)]

    with open("Stat.txt", "a+") as myfile:
        myfile.write(f"{benchmark_name} effseqnum CDF: {branch_dists_cdf} \n")


    #Aggregate for overall stats
    if branch_dists_p_aggregate is None:
        branch_dists_p_aggregate = [ x * branch_dists_sum for x in frequencies ]
    else:
        branch_dists_p_aggregate = [x + frequencies[i]*branch_dists_sum for i,x in enumerate(branch_dists_p_aggregate)]
    branch_dists_p_aggregate_sum += branch_dists_sum

    labels = [str(i) for i in range(0, max_val)]
    positions = np.arange(max_val)

    plt.figure(figsize=(fig_w, fig_h))
    plt.bar(positions, frequencies, color='blue', edgecolor='black')
    plt.xlabel('Branch distance')
    plt.ylabel('Normalised frequency')
    plt.xticks(positions[::tick_space], labels[::tick_space])
    if log_scale:
        plt.yscale('log')
    
    try:
        plt.savefig(f'trace_analysis/figures1024/{spec_benchmark}_branch_dist.png', dpi=300)
    except:
        plt.show(block=fig_block)
        print("Failed to open figure path")

    #Plot MDP takenness
    hist_str_list = ctypes.c_char_p.from_buffer(get_takenness()).value.decode('utf-8').split(',')[:-1]
    hist_counts = [float(x) for x in hist_str_list]
    hist_sum = sum(hist_counts)
    hist_p = [float(x)/hist_sum for x in hist_counts]

    #Aggregate for overall stats
    if hist_p_aggregate is None:
        hist_p_aggregate = hist_p
    else:
        hist_p_aggregate = [x + hist_p[i]*hist_sum for i,x in enumerate(hist_p_aggregate)]
    hist_p_aggregate_sum += hist_sum

    labels = [str(i/len(hist_counts)) for i in range(len(hist_counts) +1 )]
    positions = np.arange(len(hist_counts))

    plt.figure(figsize=(fig_w, fig_h))
    plt.bar(positions, hist_p, color='blue', edgecolor='black')
    plt.xlabel('Takenness')
    plt.ylabel('Normalised frequency')
    #plt.title('Histogram of takenness')
    positions = np.arange(len(hist_counts) +1) - 0.5
    plt.xticks(positions[::tick_space_hist], labels[::tick_space_hist])
    if log_scale:
        plt.yscale('log')

    try:
        plt.savefig(f'trace_analysis/figures1024/{spec_benchmark}_mdp_takenness.png', dpi=300)
    except:
        plt.show(block=fig_block)
        print("Failed to open figure path")


        #Plot path counts
    pystr = ctypes.c_char_p.from_buffer(get_path_counts()).value.decode('utf-8')
    temp = pystr.split(',')[:-1]
    #path_counts = [float(x) for x in temp][:max_val]
    path_counts = [1]
    path_counts_sum = sum(path_counts)
    path_counts_p = [float(x)/path_counts_sum for x in path_counts]

    #Aggregate for overall stats
    if path_p_aggregate is None:
        path_p_aggregate = path_counts
    else:
        path_p_aggregate = [x + path_counts[i] for i,x in enumerate(path_p_aggregate)]
    path_p_aggregate_sum += path_counts_sum

    labels = [str(i) for i in range(0, max_val)]
    positions = np.arange(max_val)

    path_counts_cdf = [f"{i}:{sum(path_counts_p[:i])}" for i, x in enumerate(path_counts_p[:1024])]

    with open("Stat.txt", "a+") as myfile:
        myfile.write(f"{benchmark_name} branch CDF: {path_counts_cdf} \n")

    plt.figure(figsize=(fig_w, fig_h))
    plt.bar(positions, path_counts_p, color='blue', edgecolor='black')
    plt.xlabel('Number of paths to load')
    plt.ylabel('Normalised frequency')
    plt.xticks(positions[::tick_space], labels[::tick_space])
    if log_scale:
        plt.yscale('log')

    try:
        plt.savefig(f'trace_analysis/figures1024/{spec_benchmark}_path_dist.png', dpi=300)
    except:
        plt.show(block=fig_block)
        print("Failed to open figure path")

        
#Print aggregate stats
labels = [str(i) for i in range(0, max_val)]
positions = np.arange(max_val)
eff_seq_dists_p_aggregate = [float(x)/eff_seq_dists_p_aggregate_sum for x in eff_seq_dists_p_aggregate]

plt.figure(figsize=(fig_w, fig_h))
plt.bar(positions, eff_seq_dists_p_aggregate, color='blue', edgecolor='black')
plt.xlabel('Linear sequence number distance')
plt.ylabel('Normalised frequency')
plt.xticks(positions[::tick_space], labels[::tick_space])
if log_scale:
    plt.yscale('log')

try:
    plt.savefig(f'trace_analysis/figures1024/aggregate_eff_seq_dist.png', dpi=300)
except:
    plt.show(block=fig_block)
    print("Failed to open figure path")

eff_seq_dist_mean = 0
for i, p in enumerate(eff_seq_dists_p_aggregate):
    eff_seq_dist_mean += i * p


eff_seq_dists_p_aggregate_cdf = [f"{i}:{sum(eff_seq_dists_p_aggregate[:i])}" for i, x in enumerate(eff_seq_dists_p_aggregate)]

with open("Stat.txt", "a+") as myfile:
    myfile.write(f"Effseqnum CDF: {eff_seq_dists_p_aggregate_cdf} \n")


eff_seq_dists_p_aggregate_cdf = [sum(eff_seq_dists_p_aggregate[:i]) for i, x in enumerate(eff_seq_dists_p_aggregate)]

plt.figure(figsize=(fig_w, fig_h))
plt.plot(positions, eff_seq_dists_p_aggregate_cdf , color='blue')
plt.xlabel('Branch distance')
plt.ylabel('Cumulative normalised frequency')
plt.xticks(positions[::tick_space], labels[::tick_space])
plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]) 
if log_scale:
    plt.yscale('log')

try:
    plt.savefig(f'trace_analysis/figures1024/aggregate_eff_seq_dist_cdf.png', dpi=300)
except:
    plt.show(block=fig_block)
    print("Failed to open figure path")

labels = [str(i) for i in range(0, max_val)]
positions = np.arange(max_val)
branch_dists_p_aggregate = [float(x)/branch_dists_p_aggregate_sum for x in branch_dists_p_aggregate]

plt.figure(figsize=(fig_w, fig_h))
plt.bar(positions, branch_dists_p_aggregate, color='blue', edgecolor='black')
plt.xlabel('Branch distance')
plt.ylabel('Normalised frequency')
plt.xticks(positions[::tick_space], labels[::tick_space])
if log_scale:
    plt.yscale('log')

try:
    plt.savefig(f'trace_analysis/figures1024/aggregate_branch_dist.png', dpi=300)
except:
    plt.show(block=fig_block)
    print("Failed to open figure path")

branch_dists_mean = 0
for i, p in enumerate(branch_dists_p_aggregate):
    branch_dists_mean += i * p

branch_dists_p_aggregate_cdf = [f"{i}:{sum(branch_dists_p_aggregate[:i])}" for i, x in enumerate(branch_dists_p_aggregate)]

with open("Stat.txt", "a+") as myfile:
    myfile.write(f"Branch CDF: {branch_dists_p_aggregate_cdf} \n")

branch_dists_p_aggregate_cdf = [sum(branch_dists_p_aggregate[:i])for i, x in enumerate(branch_dists_p_aggregate)]

plt.figure(figsize=(fig_w, fig_h))
plt.plot(branch_dists_p_aggregate_cdf, color='blue')
plt.xlabel('Branch distance')
plt.ylabel('Cumulative normalised frequency')
plt.xticks(positions[::tick_space], labels[::tick_space])

# Adjusting y-axis ticks
ax = plt.gca()
ax.yaxis.set_major_locator(MaxNLocator(5))  # Limits the number of major ticks

if log_scale:
    plt.yscale('log')

try:
    plt.savefig(f'trace_analysis/figures1024/aggregate_branch_dist_cdf.png', dpi=300)
except:
    plt.show(block=fig_block)
    print("Failed to open figure path")



labels = [str(i/len(hist_counts)) for i in range(len(hist_counts))]
positions = np.arange(len(hist_counts))
hist_p_aggregate = [float(x)/hist_p_aggregate_sum for x in hist_p_aggregate]

plt.figure(figsize=(fig_w, fig_h))
plt.bar(positions, hist_p_aggregate, color='blue', edgecolor='black')
plt.xlabel('Takenness')
plt.ylabel('Normalised Frequency')
#plt.title('Histogram of takenness')
plt.xticks(positions[::tick_space_hist], labels[::tick_space_hist])
if log_scale:
    plt.yscale('log')

try:
    plt.savefig(f'trace_analysis/figures1024/aggregate_mdp_takenness.png', dpi=300)
except:
    plt.show(block=fig_block)
    print("Failed to open figure path")

path_p_aggregate = [float(x)/path_p_aggregate_sum for x in path_p_aggregate]
labels = [str(i) for i in range(0, max_val)]
positions = np.arange(max_val)

plt.figure(figsize=(fig_w, fig_h))
plt.bar(positions, path_p_aggregate, color='blue', edgecolor='black')
plt.xlabel('Number of paths to load')
plt.ylabel('Normalised frequency')
plt.xticks(positions[::tick_space], labels[::tick_space])
if log_scale:
    plt.yscale('log')

try:
    plt.savefig(f'trace_analysis/figures1024/aggregate_path_dist.png', dpi=300)
except:
    plt.show(block=fig_block)
    print("Failed to open figure path")

#Calculate mean
path_counts_mean = 0
for i, p in enumerate(path_p_aggregate):
    path_counts_mean += i * p

path_p_aggregate_cdf = [f"{i}:{sum(path_p_aggregate[:i])}" for i, x in enumerate(path_p_aggregate)]

with open("Stat.txt", "a+") as myfile:
    myfile.write(f"Path CDF: {path_p_aggregate_cdf} \n")

path_p_aggregate_cdf = [sum(path_p_aggregate[:i])for i, x in enumerate(path_p_aggregate)]

plt.figure(figsize=(fig_w, fig_h))
plt.plot(path_p_aggregate_cdf, color='blue')
plt.xlabel('NUmber of unique paths to load')
plt.ylabel('Cumulative normalised frequency')
plt.xticks(positions[::tick_space], labels[::tick_space])

# Adjusting y-axis ticks
ax = plt.gca()
ax.yaxis.set_major_locator(MaxNLocator(5))  # Limits the number of major ticks

if log_scale:
    plt.yscale('log')

try:
    plt.savefig(f'trace_analysis/figures1024/aggregate_path_cdf.png', dpi=300)
except:
    plt.show(block=fig_block)
    print("Failed to open figure path")

with open("Stat.txt", "a+") as myfile:
    myfile.write(f"Aggregate, {eff_seq_dist_mean}, {branch_dists_mean}, {path_counts_mean} \n")



filename='shelve.out'
my_shelf = shelve.open(filename,'n') # 'n' for new

for key in dir():
    try:
        my_shelf[key] = globals()[key]
    except:
        print('ERROR shelving: {0}'.format(key))
my_shelf.close()