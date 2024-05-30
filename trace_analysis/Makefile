all: devanalysis analysislib

devanalysis: analysis.cpp
	clang++ -std=c++20 -g -O0 -o analysislib.o analysis.cpp 

analysislib: analysis.cpp
	clang++ -fPIC -shared -std=c++20 -o analysislib.so analysis.cpp 

