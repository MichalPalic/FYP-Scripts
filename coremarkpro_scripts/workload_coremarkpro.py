SPEC_PATH = "~Desktop/SPEC2017"

workloads = {}

class spec_workload:
    def __init__(self, name, args, std_inputs=None):
        self.name = name
        self.args = args
        self.std_inputs=std_inputs

    def __iter__(self):
        return iter(self.args)
    
#Coremark pro sub0benchmarks
    
benchmarks = {
    "cjepeg" : "cjpeg-rose7-preset.exe",
    "core" : "core.exe",
    "linalg" : "linear_alg-mid-100x100-sp.exe",
    "loops" : "loops-all-mid-10k-sp.exe",
    "nnet": "nnet_test.exe",
    "parser" : "parser-125k.exe",
    "radix2" : "radix2-big-64k.exe",
    "sha" : "sha-test.exe",
    "zip" : "zip-test.exe"
}

args = [["-v0", "-c1", "-w1", "-i1"]]

workloads["cjpeg"] = spec_workload("cjpeg-rose7-preset.exe", 
                                                     args)

workloads["core"] = spec_workload("core.exe", 
                                      args)

workloads["linalg"] = spec_workload("linear_alg-mid-100x100-sp.exe", 
                                                           args)

workloads["loops"] = spec_workload("loops-all-mid-10k-sp.exe",
                                                      args)

workloads["nnet"] = spec_workload("nnet_test.exe",
                                           args)

workloads["parser"] = spec_workload("parser-125k.exe",
                                              args)

workloads["radix2"] = spec_workload("radix2-big-64k.exe",
                                                args)

workloads["sha"] = spec_workload("sha-test.exe",
                                          args)

workloads["zip"] = spec_workload("zip-test.exe", 
                                          args)
