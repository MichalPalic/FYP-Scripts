all: devanalysis analysislib

devanalysis: analysis.cpp
	clang++ -std=c++20 -g -O0 -lboost_iostreams -lzstd -o analysislib.o analysis.cpp 

analysislib: analysis.cpp
	clang++ -fPIC -shared -std=c++20 -lboost_iostreams -lzstd -o analysislib.so analysis.cpp 

