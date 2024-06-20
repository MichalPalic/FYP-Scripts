import sys
import matplotlib.pyplot as plt
import numpy as np
import ctypes
import os

path = os.getcwd()
#cpplibrary = ctypes.CDLL(os.path.join(path, "analysislib.so"))
cpplibrary = ctypes.CDLL(os.path.join(path, "/home/michal/Desktop/fyp_scripts/trace_analysis/analysislib.so"))

calculate_statistics = cpplibrary.calculate_statistics
calculate_statistics.argtypes = [ctypes.c_char_p]

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


calculate_statistics(b'/home/michal/Downloads/sha100k.csv.zst')
#calculate_statistics(b'/home/michal/Desktop/coremarkpro_trace/radix2/full_trace.csv')

#Plot eff seq number dists
pystr = ctypes.c_char_p.from_buffer(get_eff_seq_dists()).value.decode('utf-8')
temp = pystr.split(',')[:-1]
eff_seq_dists = [int(x.split(':')[0]) for x in temp]
eff_seq_dists_counts = [int(x.split(':')[1]) for x in temp]
eff_seq_dists_sum = sum(eff_seq_dists_counts)
eff_seq_dists_p = [float(x)/eff_seq_dists_sum for x in eff_seq_dists_counts]

max_val = 30

frequencies = eff_seq_dists_counts[:max_val]
labels = [str(i) for i in eff_seq_dists[:max_val]]
positions = np.arange(max_val)
plt.bar(positions, frequencies, color='blue', edgecolor='black')
plt.xlabel('Bins')
plt.ylabel('Frequency')
plt.title('Histogram of committed sequence number distances')
plt.xticks(positions, labels)
plt.yscale('log')
plt.show(block=True)

#Plot seq number dists
pystr = ctypes.c_char_p.from_buffer(get_seq_dists()).value.decode('utf-8')
temp = pystr.split(',')[:-1]
seq_dists = [int(x.split(':')[0]) for x in temp]
seq_dists_counts = [int(x.split(':')[1]) for x in temp]
seq_dists_sum = sum(seq_dists_counts)
seq_dists_p = [float(x)/seq_dists_sum for x in seq_dists_counts]

frequencies = seq_dists_counts[:max_val]
labels = [str(i) for i in seq_dists[:max_val]]
positions = np.arange(max_val)
plt.bar(positions, frequencies, color='blue', edgecolor='black')
plt.xlabel('Bins')
plt.ylabel('Frequency')
plt.title('Histogram of sequence number distances')
plt.xticks(positions, labels)
plt.yscale('log')
plt.show(block=True)

#Plot branch dists
pystr = ctypes.c_char_p.from_buffer(get_branch_dists()).value.decode('utf-8')
temp = pystr.split(',')[:-1]
branch_dists = [int(x.split(':')[0]) for x in temp]
branch_dists_counts = [int(x.split(':')[1]) for x in temp]
branch_dists_sum = sum(branch_dists_counts)
branch_dists_p = [float(x)/branch_dists_sum for x in branch_dists_counts]

frequencies = branch_dists_counts[:max_val]
labels = [str(i) for i in branch_dists[:max_val]]
positions = np.arange(max_val)
plt.bar(positions, frequencies, color='blue', edgecolor='black')
plt.xlabel('Bins')
plt.ylabel('Frequency')
plt.title('Histogram of branch distances')
plt.xticks(positions, labels)
plt.yscale('log')
plt.show(block=True)


#Plot MDP takenness
hist_str_list = ctypes.c_char_p.from_buffer(get_takenness()).value.decode('utf-8').split(',')[:-1]
hist_counts = [int(x) for x in hist_str_list]
hist_sum = sum(branch_dists_counts)
hist_p = [float(x)/branch_dists_sum for x in branch_dists_counts]

labels = [str(i) for i in range(len(hist_counts))]
positions = np.arange(len(hist_counts))
plt.bar(positions, hist_counts, color='blue', edgecolor='black')
plt.xlabel('Bins')
plt.ylabel('Frequency')
plt.title('Histogram of takenness')
plt.xticks(positions, labels)
plt.yscale('log')
plt.show(block=True)
