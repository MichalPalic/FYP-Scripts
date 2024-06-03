import sys
import matplotlib.pyplot as plt
import numpy as np
import ctypes
import os
import glob


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

clear_all = cpplibrary.clear_all
clear_caches = cpplibrary.clear_caches

#Control parameters
fig_block = False
fig_h = 4
fig_w = 14
max_val = 120
tick_space = 5

checkpoint_dir = "/home/michal/Desktop/spec_2017_rate_checkpoints"
trace_dir = "/home/michal/Desktop/windows/FYP/spec_2017_rate_trace"
result_dir = "/home/michal/Desktop/windows/FYP/spec_2017_rate_results"

weight_paths = glob.glob(checkpoint_dir + "/**/simpoints.weights", recursive=True)
weight_paths.sort()

spec_benchmarks = list(set([weight_path.split('/')[-3] for weight_path in weight_paths]))
spec_benchmarks.sort()
spec_benchmarks = reversed(spec_benchmarks)

for spec_benchmark in spec_benchmarks:
    #Completely reset backend state between benchmarks
    clear_all()

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

            #Break backend dependencies between checkpoints
            clear_caches()

            trace_path = f"{trace_dir}/{benchmark_name}/{benchmark_idx}/{checkpoint_idx}/full_trace.csv.zst"

            # if not os.path.isfile(trace_path):
            #     continue

            print(f"Aggregating statistics for: {trace_path} with weight {weight}")
            calculate_statistics(trace_path.encode(encoding="ascii",errors="ignore"), float(weight), 1000000)

    print(f"Dumping graphs for: {trace_path}")

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
            frequencies[dist-1] = eff_seq_dists_counts[idx]
    
    labels = [str(i) for i in range(1, max_val+1)]
    positions = np.arange(max_val)

    plt.figure(figsize=(fig_w, fig_h))
    plt.bar(positions, frequencies, color='blue', edgecolor='black')
    plt.xlabel('Linear sequence number distance')
    plt.ylabel('Relative Frequency')
    plt.xticks(positions[::tick_space], labels[::tick_space])
    plt.yscale('log')

    try:
        plt.savefig(f'trace_analysis/figures/{spec_benchmark}_eff_seq_dist.png', dpi=300)
    except:
        plt.show(block=fig_block)
        print("Failed to open figure path")

    #Plot seq number dists
    pystr = ctypes.c_char_p.from_buffer(get_seq_dists()).value.decode('utf-8')
    temp = pystr.split(',')[:-1]
    seq_dists = [int(x.split(':')[0]) for x in temp]
    seq_dists_counts = [float(x.split(':')[1]) for x in temp]
    seq_dists_sum = sum(seq_dists_counts)
    seq_dists_p = [float(x)/seq_dists_sum for x in seq_dists_counts]

    frequencies = [0 for  i in range(max_val)]
    for idx, dist in enumerate(seq_dists[1:max_val+1]):
        if dist < max_val + 1:
            frequencies[dist-1] = seq_dists_counts[idx]

    labels = [str(i) for i in range(1, max_val+1)]
    positions = np.arange(max_val)

    plt.figure(figsize=(fig_w, fig_h))
    plt.bar(positions, frequencies, color='blue', edgecolor='black')
    plt.xlabel('Sequence number distance')
    plt.ylabel('Relative Frequency')
    plt.xticks(positions[::tick_space], labels[::tick_space])
    plt.yscale('log')

    try:
        plt.savefig(f'trace_analysis/figures/{spec_benchmark}_seq_dist.png', dpi=300)
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
            frequencies[dist] = branch_dists_counts[idx]

    labels = [str(i) for i in range(max_val)]
    positions = np.arange(max_val)

    plt.figure(figsize=(fig_w, fig_h))
    plt.bar(positions, frequencies, color='blue', edgecolor='black')
    plt.xlabel('Branch distance')
    plt.ylabel('Relative Frequency')
    plt.xticks(positions[::tick_space], labels[::tick_space])
    plt.yscale('log')
    
    try:
        plt.savefig(f'trace_analysis/figures/{spec_benchmark}_branch_dist.png', dpi=300)
    except:
        plt.show(block=fig_block)
        print("Failed to open figure path")

    #Plot MDP takenness
    hist_str_list = ctypes.c_char_p.from_buffer(get_takenness()).value.decode('utf-8').split(',')[:-1]
    hist_counts = [float(x) for x in hist_str_list]
    hist_sum = sum(branch_dists_counts)
    hist_p = [float(x)/branch_dists_sum for x in branch_dists_counts]

    labels = [str(i/len(hist_counts)) for i in range(len(hist_counts))]
    positions = np.arange(len(hist_counts))

    plt.figure(figsize=(fig_w, fig_h))
    plt.bar(positions, hist_counts, color='blue', edgecolor='black')
    plt.xlabel('Takenness')
    plt.ylabel('Relative Frequency')
    #plt.title('Histogram of takenness')
    plt.xticks(positions[::tick_space], labels[::tick_space])
    plt.yscale('log')

    try:
        plt.savefig(f'trace_analysis/figures/{spec_benchmark}_mdp_takenness.png', dpi=300)
    except:
        plt.show(block=fig_block)
        print("Failed to open figure path")
        
