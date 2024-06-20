import argparse
import os
import subprocess
import statistics

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

#Generate plot
def make_plot(row_labels, col_labels, data):
    cmap = LinearSegmentedColormap.from_list("red_to_green", ["red", "green"])
    # Create the plot
    plt.figure(figsize=(10, 8))
    ax = plt.gca()
    im = ax.imshow(data, cmap=cmap, interpolation='nearest')

    # Setting tick marks on axes
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))

    # Labeling tick marks
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Set labels for axes
    plt.xlabel('Column Index')
    plt.ylabel('Row Index')

    # Rotate x labels for better display
    plt.xticks(rotation=45)

    # Adding the text annotations
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            text = ax.text(j, i, f'{data[i, j]:.5f}',
                        ha='center', va='center', color='white')

    # Show color scale
    plt.colorbar(im)
    plt.title('Matrix Visualization from Red to Green with Cell Values')
    plt.show(block=True)



parser = argparse.ArgumentParser(
                prog='Coremarkpro statscript',
                description='Extracts stats from run directory')


parser.add_argument('--statdir',
                type=str,
                default="/home/michal/Desktop/coremarkpro_store_set_sweep",
                help='Path to Stat folder to be traversed')

parser.add_argument('--statname',
                type=str,
                default="system.cpu.numCycles",
                help='Stat name to be searched for in file')


args = parser.parse_args()

#Ensure absolute paths
args.statdir = os.path.abspath(args.statdir)

with open("temp.log", 'w+') as log:
    process = subprocess.Popen(["ag", f"{args.statname}"], stdout=log, stderr=log, cwd=args.statdir)
    (output, err) = process.communicate()  
    p_status = process.wait()

with open("temp.log", 'r') as agout:
    lines = agout.readlines()

configname = ""
sub_bench = ""
data_dict = {}

for line in lines:
    #Strip Comment
    linetmp = line.split('#')[0]
    linetmp = linetmp.split(' ')

    linestrip = []

    for linetmpelem in linetmp:
        if linetmpelem == '':
            continue
        else:
            linestrip.append(linetmpelem)

    sub_bench = linestrip[0].split(':')[0].split('/')[-2].strip()
    configuration = linestrip[0].split(':')[0].split('/')[-3].strip()

    value = int(linestrip[1])

    if not configuration in data_dict:
        data_dict[configuration]={}
    
    data_dict[configuration][sub_bench] = value


#Dump matrix onto stdout

print("Total matrix") 
configuration_keys  =  list(data_dict.keys())
configuration_keys.sort()

sub_bench_keys = []
for inner_dict_key in data_dict:
    inner_dict = data_dict[inner_dict_key]
    sub_bench_keys.extend(list(inner_dict.keys()))

sub_bench_keys = list(set(sub_bench_keys))
sub_bench_keys.sort()
print(',' + ','.join(sub_bench_keys))

for configuration_key in configuration_keys:
    outstr = configuration_key + ","
    for sub_bench_key in sub_bench_keys:
        if sub_bench_key in data_dict[configuration_key]:
            outstr += str(data_dict[configuration_key][sub_bench_key]) + ","
        else:
            outstr += str(-1) + ","
    
    print(outstr)


print("Average matrix") 
configuration_keys  =  list(data_dict.keys())
configuration_keys.sort()

configuration_keys_1 = list(set([int(cfg_key.split('_')[0]) for cfg_key in configuration_keys]))
configuration_keys_1.sort()
configuration_keys_2 = list(set([int(cfg_key.split('_')[1]) for cfg_key in configuration_keys]))
configuration_keys_2.sort()

print(',' + ','.join([str(k) for k in configuration_keys_2]))

i = 0
refval = 0
outarr = np.zeros((len(configuration_keys_1), len(configuration_keys_2)))
for cfg_key_1 in configuration_keys_1:
    outstr = str(cfg_key_1) + ","

    j = 0
    for cfg_key_2 in configuration_keys_2:
        if not f"{cfg_key_1}_{cfg_key_2}" in data_dict:
            j += 1
            continue

        d = data_dict[f"{cfg_key_1}_{cfg_key_2}"]

        mean = statistics.mean([d[k] for k in d])
        outstr += str(mean) + ","

        if j == 0 and i == 0:
            refval = mean

        outarr[i][j] = float((mean - refval))/refval

        j += 1
    i += 1
    print (outstr)

make_plot(configuration_keys_1, configuration_keys_2, outarr)