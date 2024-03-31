SPEC_PATH = "~Desktop/SPEC2017"

workloads = {}

class spec_workload:
    def __init__(self, name, args, std_inputs=None):
        self.name = name
        self.args = args
        self.std_inputs=std_inputs

    def __iter__(self):
        return iter(self.args)
    
#Spec rate
    
benchmarks = {
    #Integer benchmarks
    "perlbench" : "500.perlbench_r",
    "gcc" : "502.gcc_r",
    "mcf" : "505.mcf_r",
    "omnetpp" : "520.omnetpp_r",
    "xalancbmk" : "523.xalancbmk_r",
    "x264" : "525.x264_r",
    "deepsjeng" : "531.deepsjeng_r",
    "leela" : "541.leela_r",
    "exchange2" : "548.exchange2_r",
    "xz" : "557.xz_r",

    #Floating point benchmarks
    "bwaves" : "503.bwaves_r",
    "cactuBSSN" : "507.cactuBSSN_r",
    "namd" : "508.namd_r",
    "namd" : "510.parest_r",
    "namd" : "511.povray_r",
    "lbm" : "519.lbm_r",
    "wrf" : "521.wrf_r",
    "blender" : "526.blender_r",
    "cam4" : "527.cam4_r",
    "imagick" : "538.imagick_r",
    "nab" : "544.nab_r",
    "fotonik3d" : "549.fotonik3d_r",
    "roms": "554.roms_r",
}

args = [
    ["-I./lib", "checkspam.pl", "2500", "5", "25", "11", "150", "1", "1", "1", "1"],
    ["-I./lib", "diffmail.pl", "4", "800", "10", "17", "19", "300"],
    ["-I./lib", "splitmail.pl", "6400", "12", "26", "16", "100", "0"],
]
workloads["500.perlbench_r"] = spec_workload("500.perlbench_r", args)

args = [
    ["gcc-pp.c", "-O3", "-finline-limit=0", "-fif-conversion", "-fif-conversion2", "-o", "gcc-pp.opts-O3_-finline-limit_0_-fif-conversion_-fif-conversion2.s"],
    ["gcc-pp.c", "-O2", "-finline-limit=36000", "-fpic", "-o", "gcc-pp.opts-O2_-finline-limit_36000_-fpic.s"],
    ["gcc-smaller.c", "-O3", "-fipa-pta", "-o", "gcc-smaller.opts-O3_-fipa-pta.s"],
    ["ref32.c", "-O5", "-o", "ref32.opts-O5.s"],
    ["ref32.c", "-O3", "-fselective-scheduling", "-fselective-scheduling2", "-o", "ref32.opts-O3_-fselective-scheduling_-fselective-scheduling2.s"],
]
workloads["502.gcc_r"] = spec_workload("502.gcc_r", args)

workloads["505.mcf_r"] = spec_workload("505.mcf_r", [["inp.in"]])

workloads["520.omnetpp_r"] = spec_workload("520.omnetpp_r", [["-c", "General", "-r", "0"]])

workloads["523.xalancbmk_r"] = spec_workload("523.xalancbmk_r", [["-v", "t5.xml", "xalanc.xsl"]])

args = [
    ["--pass", "1", "--stats", "x264_stats.log", "--bitrate", "1000", 
    "--frames", "1000", "-o", "BuckBunny_New.264", "BuckBunny.yuv", "1280x720"],
    ["--pass", "2", "--stats", "x264_stats.log", "--bitrate", "1000",
        "--dumpyuv", "200", "--frames", "1000", "-o", "BuckBunny_New.264", "BuckBunny.yuv", "1280x720"],
    ["--seek", "500", "--dumpyuv", "200", "--frames", "1250", "-o", "BuckBunny_New.264", "BuckBunny.yuv", "1280x720"]
]
workloads["525.x264_r"] = spec_workload("525.x264_r", args)

args = [
    ["ref.txt"]
]
workloads["531.deepsjeng_r"] = spec_workload("531.deepsjeng_r", args)

args = [
    ["ref.sgf"]
]
workloads["541.leela_r"] = spec_workload("541.leela_r", args)

args = [
    ["6"]
]
workloads["548.exchange2_r"] = spec_workload("548.exchange2_r", args)

args = [
    ["cld.tar.xz", "160", "19cf30ae51eddcbefda78dd06014b4b96281456e078ca7c13e1c0c9e6aaea8dff3efb4ad6b0456697718cede6bd5454852652806a657bb56e07d61128434b474",
    "59796407", "61004416", "6"],
    ["cpu2006docs.tar.xz", "250",
    "055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae",
    "23047774", "23513385", "6e"],
    ["input.combined.xz", "250", "a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf",
    "40401484", "41217675", "7"],
]
workloads["557.xz_r"] = spec_workload("557.xz_r", args)


#Floating point benchmarks
args = [["bwaves_1"], ["bwaves_2"], ["bwaves_3"], ["bwaves_4"]]
infiles = ["bwaves_1.in","bwaves_2.in", "bwaves_3.in","bwaves_4.in"]
workloads["503.bwaves_r"] = spec_workload("503.bwaves_r", args, infiles)

args = [
    ["spec_ref.par"]
]
workloads["507.cactuBSSN_r"] = spec_workload("507.cactuBSSN_r", args)

args = [
    ["--input", "apoa1.input", "--output", "apoa1.ref.output", "--iterations", "65"]
]
workloads["508.namd_r"] = spec_workload("508.namd_r", args)

workloads["510.parest_r"] = spec_workload("510.parest_r", [["ref.prm"]])

workloads["511.povray_r"] = spec_workload("511.povray_r", [["SPEC-benchmark-ref.ini"]])

args = [["3000", "reference.dat", "0", "0", "100_100_130_ldc.of"]]
workloads["519.lbm_r"] = spec_workload("519.lbm_r", args)

workloads["521.wrf_r"] = spec_workload("521.wrf_r", [[]])

args = [
    ["sh3_no_char.blend", "--render-output", "sh3_no_char_", "--threads", "1", "-b", "-F", "RAWTGA", "-s", "849", "-e", "849", "-a"]
]
workloads["526.blender_r"] = spec_workload("526.blender_r", args)

workloads["527.cam4_r"] = spec_workload("527.cam4_r", [[]])

args = [
    ["-limit", "disk", "0", "refrate_input.tga", "-edge", "41", "-resample",
    "181%", "-emboss", "31", "-colorspace", "YUV", "-mean-shift", "19x19+15%",
    "-resize", "30%", "refrate_output.tga"]
]
workloads["538.imagick_r"] = spec_workload("538.imagick_r", args)

workloads["544.nab_r"] = spec_workload("544.nab_r", [["1am0", "1122214447", "122"]])

workloads["549.fotonik3d_r"] = spec_workload("549.fotonik3d_r", [[]])

workloads["554.roms_r"] = spec_workload("554.roms_r", [[]], ["ocean_benchmark2.in.x"])


#Spec speed

# benchmarks = {
#     #Integer benchmarks
#     "perlbench" : "600.perlbench_s",
#     "gcc" : "602.gcc_s",
#     "mcf" : "605.mcf_s",
#     "omnetpp" : "620.omnetpp_s",
#     "xalancbmk" : "623.xalancbmk_s",
#     "x264" : "625.x264_s",
#     "deepsjeng" : "631.deepsjeng_s",
#     "leela" : "641.leela_s",
#     "exchange2" : "648.exchange2_s",
#     "xz" : "657.xz_s",

#     #Floating point benchmarks
#     "bwaves" : "603.bwaves_s",
#     "cactuBSSN" : "607.cactuBSSN_s",
#     "lbm" : "619.lbm_s",
#     "wrf" : "621.wrf_s",
#     "cam4" : "627.cam4_s",
#     "pop2" : "628.pop2_s",
#     "imagick" : "638.imagick_s",
#     "nab" : "644.nab_s",
#     "fotonik3d" : "649.fotonik3d_s",
#     "roms": "654.roms_s",
# }

args = [
    ["-I./lib", "checkspam.pl", "2500", "5", "25", "11", "150", "1", "1", "1", "1"],
    ["-I./lib", "diffmail.pl", "4", "800", "10", "17", "19", "300"],
    ["-I./lib", "splitmail.pl", "6400", "12", "26", "16", "100", "0"],
]
workloads["600.perlbench_s"] = spec_workload("600.perlbench_s", args)

args = [
    ["-O5", "-fipa-pta"],
    ["-O5", "-finline-limit=1000", "-fselective-scheduling", "-fselective-scheduling2"],
    ["-O5", "-finline-limit=24000", "-fgcse", "-fgcse-las", "-fgcse-lm", "-fgcse-sm"],
]
workloads["602.gcc_s"] = spec_workload("602.gcc_s", args)

workloads["605.mcf_s"] = spec_workload("605.mcf_s", [["inp.in"]])

workloads["620.omnetpp_s"] = spec_workload("620.omnetpp_s", [["-c", "General", "-r", "0"]])

workloads["623.xalancbmk_s"] = spec_workload("623.xalancbmk_s", [["-v", "t5.xml", "xalanc.xsl"]])

args = [
    ["--pass", "1", "--stats", "x264_stats.log", "--bitrate", "1000", 
        "--frames", "1000", "-o", "BuckBunny_New.264", "BuckBunny.yuv", "1280x720"],
    ["--pass", "2", "--stats", "x264_stat2.log", "--bitrate", "1000",
        "--dumpyuv", "200", "--frames", "1000", "-o", "BuckBunny_New.264", "BuckBunny.yuv", "1280x720"],
    ["--seek", "500", "--dumpyuv", "200", "--frames", "1250", "-o", "BuckBunny_New.264", "BuckBunny.yuv", "1280x720"]
]
workloads["625.x264_s"] = spec_workload("625.x264_s", args)

args = [
    ["ref.txt"]
]
workloads["631.deepsjeng_s"] = spec_workload("631.deepsjeng_s", args)

args = [
    ["ref.sgf"]
]
workloads["641.leela_s"] = spec_workload("641.leela_s", args)

args = [
    ["6"]
]
workloads["648.exchange2_s"] = spec_workload("648.exchange2_s", args)

args = [
    ["cpu2006docs.tar.xz", "6643",
    "055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae",
    "1036078272", "1111795472", "4"],
    ["cld.tar.xz", "1400", "19cf30ae51eddcbefda78dd06014b4b96281456e078ca7c13e1c0c9e6aaea8dff3efb4ad6b0456697718cede6bd5454852652806a657bb56e07d61128434b474",
    "536995164", "539938872", "8"]
]
workloads["657.xz_s"] = spec_workload("657.xz_s", args)


#Floating point benchmarks
args = [["bwaves_1"], ["bwaves_2"]]
infiles = [["bwaves_1.in"],["bwaves_2.in"]]
workloads["603.bwaves_s"] = spec_workload("603.bwaves_s", args, infiles)

args = [
    ["spec_ref.par"]
]
workloads["607.cactuBSSN_s"] = spec_workload("607.cactuBSSN_s", args)

args = [["2000", "reference.dat", "0", "0", "200_200_260_ldc.of"]]
workloads["619.lbm_s"] = spec_workload("619.lbm_s", args)

workloads["621.wrf_s"] = spec_workload("621.wrf_s", [[]])

workloads["627.cam4_s"] = spec_workload("627.cam4_s", [[]])

workloads["628.pop2_s"] = spec_workload("628.pop2_s", [[]])

args = [
    ["-limit", "disk", "0", "refspeed_input.tga", "-resize", "817%", "-rotate",
        "-2.76", "-shave", "540x375", "-alpha", "remove", "-auto-level",
        "-contrast-stretch", "1x1%", "-colorspace", "Lab", "-channel", "R",
        "-equalize", "+channel", "-colorspace", "sRGB", "-define",
        "histogram:unique-colors=false", "-adaptive-blur", "0x5", "-despeckle",
        "-auto-gamma", "-adaptive-sharpen", "55", "-enhance",
        "-brightness-contrast", "10x10", "-resize 30%", "refspeed_output.tga"]
]
workloads["638.imagick_s"] = spec_workload("638.imagick_s", args)

workloads["644.nab_s"] = spec_workload("644.nab_s", [["3j1n", "20140317", "220"]])

workloads["649.fotonik3d_s"] = spec_workload("649.fotonik3d_s", [[]])

workloads["654.roms_s"] = spec_workload("654.roms_s", [[]], ["ocean_benchmark3.in"])







  


