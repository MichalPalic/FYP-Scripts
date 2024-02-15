# SPEC2017_Simpoint_Scripts

Setup symlinks for config files
ln -s ~/Desktop/SPEC2017_Simpoint_Scripts/SPEC2017/gcc-linux-x86.cfg ~/Desktop/SPEC2017/config/gcc-linux-x86.cfg
ln -s ~/Desktop/SPEC2017_Simpoint_Scripts/SPEC2017/Clang-linux-x86.cfg ~/Desktop/SPEC2017/config/Clang-linux-x86.cfg

ln -s ~/Desktop/gem5/configs/fyp/x86_gen_bbv.py ~/Desktop/SPEC2017_Simpoint_Scripts/Gem5_config/x86_gen_bbv.py


runcpu --config=gcc-linux-x86.cfg --action=build intspeed
