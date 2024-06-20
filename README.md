# SPEC2017_Simpoint_Scripts


## Generating checkpoints
One of the main contributions of this repository are the set of scripts
for efficiciently generating the checkpoints for SPECRate CPU 2017 using SimPoint.
Expect 1-2 days of runtime on a reasonable computer.

### Step 1: Extract the SPEC run directories:
Set up a symlink to the configuration file(s) in this repo
    ln -s {Path to repo}/spec_configs/gcc-linux-x86.cfg {path to SPEC 2017 install}/SPEC2017/config/gcc-linux-x86.cfg

Use the following commands to execute the benchmark suite
    runcpu --config=gcc-linux-x86.cfg --action=run intrate
    runcpu --config=gcc-linux-x86.cfg --action=run fprate
    
Afterwards take the run directories containing the executables and re-package
them into the following directory structure:

Top level name     Benchmark     Everything eles
spec_executables/500.perlbench/{run_dir_files}

The result is a minimal executable bundle necessary to run the benchmark.

### Step 2: Generate BBVS with the valgrind_bbv.py
You must have an up to date valgrind version installed.

    python3 valgrind_bbv.py 
        --specexe {Path to executable bundle} 
        --workdir {Directory to generate checkpoints in}

### Step 3: Cluster BBVs
Apply simpoints to bbvs to determine which should be kept as SimPoints. Requires
the SimPoint binary to be compiled.
We suggest the following repository that maintains a version of this software.
https://github.com/hanhwi/SimPoint

    python3 simpoint_clustering.py 
        --simpointbin {Path SimPoints executable}
        --workdir {Directory to generate checkpoints in}

Step 4: Use Kvm to generate checkpoints
Note that the flow has only been tested on commit 10dbfb8, but should work past 
10dbfb8. We suggest that you just use the head of the develop branch.

In case of errors please follow the gem5 setup guide for Kvm to install the
dependencies, and the additional notes withing the script on specific errors
and their solutions.

    python3  gen_checkpoints.py 
        --gem5dir {Path gem5 executable}
        --workdir {Directory to generate checkpoints in}
        --specexe {Path to executable bundle} 

### Step 4: Run checkpoints.

Note that there are hardcoded paths in the checkpoint files, so do not move
the checkpoint or result directories, or you might get errors for the execution of 
ca. 10\% of the checkpoints

    python3  gen_checkpoints.py 
    --gem5dir {Path gem5 executable}
    --checkpointddir {Directory containing checkpoints}
    --resultdir {Directory to store results in}
    --specexe {Path to executable bundle}

### Step 5: Process results.
To aggregate the results see one of our analysis scripts 
eg. spec_analysis/compare_state.py

All done!

## Some of the most important graphs from the report
Coremark store set scaling: see coremarkpro_analysis/run_coremarkpro_storeset_clear_sample.py
Oracle performance: see spec_analysis/oracle_perf.py
Memory conflict checking granularity: see spec_analysis/sweep_depshift.py
                                        spec_analysis/process_depshift_stats.py
Trace statistic distributions: see trace_analyis/spec_analysis.py