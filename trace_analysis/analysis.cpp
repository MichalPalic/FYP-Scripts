#include <fstream>
#include <iostream>
#include <list>
#include <map>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>
#include <cassert>
#include <string.h>

#include <boost/iostreams/device/file.hpp>
#include <boost/iostreams/filtering_stream.hpp>
#include <boost/iostreams/filter/zstd.hpp>
#include <iostream>
#include <string>

//Common helper classes
//Setup to allow TraceUID to be used as hashmap key
struct TraceUID
{
  uint64_t pc;
  uint64_t n_visited;

  TraceUID(){}
  TraceUID(uint64_t pc, uint64_t n_visited): pc(pc), n_visited(n_visited){}

  bool operator==(const TraceUID &other) const
    {
      return (pc == other.pc && n_visited == other.n_visited);
    }

  bool operator<(const TraceUID &other) const
  {
    return pc == other.pc ? n_visited < other.n_visited : pc < other.pc;
  }
};

  template<>
  struct std::hash<TraceUID>
  {
    std::size_t operator()(const TraceUID& t) const noexcept
    {
      std::size_t h1 = std::hash<uint64_t>{}(t.pc);
      std::size_t h2 = std::hash<uint64_t>{}(t.n_visited);
      return h1 ^ (h2 << 1);
    }
  };

  namespace std {
    string to_string(const TraceUID &t);
  }


struct trace_elem
{
    bool valid;
    bool load;
    TraceUID tuid;
    TraceUID dep;
    uint64_t seqNum;
    uint64_t effSeqNum;
    uint64_t mem_addr;

  trace_elem(){}
  trace_elem( 
    bool _valid,
    bool _load,
    TraceUID _tuid,
    TraceUID _dep,
    uint64_t _seqNum,
    uint64_t _effSeqNum,
    uint64_t _mem_addr): 
    valid(_valid), load(_load), tuid(_tuid), dep(_dep), seqNum(_seqNum), 
    effSeqNum(_effSeqNum), mem_addr(_mem_addr){}
};

  //Tuple holds bool:  Valid (bool), Load(true)/store(false),
  //this pc/access_number, pc/access_number dependent, sequence_number,
  //eff_sequence_number mem_addr

// using full_trace_T = std::tuple<bool, bool, TraceUID, TraceUID, uint64_t,
//       uint64_t, uint64_t>;

std::vector<trace_elem> trace;

  void load_trace(boost::iostreams::filtering_istream& infile, uint64_t n){
      std::string line;

      if (infile.fail()){
          printf("Failed to open mem trace path \n");
          return;
      }

      uint64_t line_n = 0;
      while (std::getline(infile, line) && line_n < n)
      {
          //Allow for comments to be ignored
          if (line[0] == '#'){
              continue;
          }

          bool valid;
          bool load;
          TraceUID tuid;
          TraceUID dep;
          uint64_t seqNum;
          uint64_t effSeqNum;
          uint64_t mem_addr;

          uint64_t pc,n_visited;

          std::string temp;
          std::stringstream ss(line);

          std::getline(ss, temp, ',');
          valid = std::stoull(temp);

          std::getline(ss, temp, ',');
          load = std::stoull(temp);

          std::getline(ss, temp, ':');
          pc = std::stoull(temp);

          std::getline(ss, temp, ',');
          n_visited = std::stoull(temp);

          tuid = TraceUID(pc, n_visited);

          std::getline(ss, temp, ':');
          pc = std::stoull(temp);

          std::getline(ss, temp, ',');
          n_visited = std::stoull(temp);

          dep = TraceUID(pc, n_visited);

          std::getline(ss, temp, ',');
          seqNum = std::stoull(temp);

          std::getline(ss, temp, ',');
          effSeqNum = std::stoull(temp);

          std::getline(ss, temp, ',');
          mem_addr = std::stoull(temp);

          trace.push_back(
              trace_elem(valid, load, tuid, dep, seqNum, effSeqNum, mem_addr>>4));

          line_n++;
      }
  };

  //Address to seqnum distance
  std::map<uint64_t, uint64_t> seqDist;
  std::unordered_map<uint64_t, uint64_t> seqDistCache;

  //Address to effective seqnum distance
  std::map<uint64_t, uint64_t> effSeqDist;
  std::unordered_map<uint64_t, uint64_t> effSeqDistCache;

  //Address to effective seqnum distance
  uint64_t global_branch_n;
  std::map<uint64_t, uint64_t> branchDist;
  std::unordered_map<uint64_t, uint64_t> branchDistCache;

  //Pc -> Pc + count relation
  //Backwards address cache address -> PC
  std::unordered_map<uint64_t, uint64_t> pairCache;
  std::unordered_map<uint64_t, std::unordered_map<uint64_t, uint64_t>> pairCounts;

  void traverse(){

      for(auto i =  trace.begin(); i != trace.end(); i++){

          trace_elem elem = *i;

          //Normal store
          if(!elem.load){
              seqDistCache[elem.mem_addr] = elem.seqNum;
              effSeqDistCache[elem.mem_addr] = elem.effSeqNum;

              branchDistCache[elem.mem_addr] = global_branch_n; 
              pairCache[elem.mem_addr] = elem.tuid.pc;


          //Normal load
          } else if(elem.load && elem.valid){
                
                //Log seq distance 
                uint64_t distance = 0;
                if (seqDistCache.contains(elem.mem_addr))
                    distance = elem.seqNum - seqDistCache[elem.mem_addr];
                else 
                    distance = 0;
                
                if (seqDist.contains(distance))
                    seqDist[distance]++;
                else
                    seqDist[distance] = 1;

                //Log eff seq distance 
                if (effSeqDistCache.contains(elem.mem_addr))
                    distance = elem.effSeqNum - effSeqDistCache[elem.mem_addr];
                else 
                    distance = 0;
                
                if (effSeqDist.contains(distance))
                    effSeqDist[distance]++;
                else
                    effSeqDist[distance] = 1;

                //Log eff seq distance 
                if (effSeqDistCache.contains(elem.mem_addr))
                    distance = elem.effSeqNum - effSeqDistCache[elem.mem_addr];
                else 
                    distance = 0;
                
                if (effSeqDist.contains(distance))
                    effSeqDist[distance]++;
                else
                    effSeqDist[distance] = 1;
                
                //Log branch distance 
                if (branchDistCache.contains(elem.mem_addr))
                    distance = global_branch_n - branchDistCache[elem.mem_addr];
                else 
                    distance = uint64_t(-1);
                
                if (branchDist.contains(distance))
                    branchDist[distance]++;
                else
                    branchDist[distance] = 1;

                uint64_t pc = 0;
                if (pairCache.contains(elem.mem_addr))
                    pc = pairCache[elem.mem_addr];
                else
                    pc = 0;
        
                if (pairCounts[elem.tuid.pc].contains(pc))
                    pairCounts[elem.tuid.pc][pc] ++;
                else
                    pairCounts[elem.tuid.pc][pc] = 1;

          //Branch 
          } else if (elem.load && !elem.valid){
            global_branch_n++;

          } else {
            assert(false);
          }

      }

  }

//Please don't mangle my symbols so that I can call you from python 👉👈
extern "C"{
  char* get_seq_dists(){
    std::string out = "";

    for ( auto dist : seqDist){
        out += std::to_string(dist.first);
        out +=':';
        out += std::to_string(dist.second);
        out +=',';
    }

    return strdup(out.c_str());
  }

  char* get_eff_seq_dists(){
    std::string out = "";

    for ( auto dist : effSeqDist){
        out += std::to_string(dist.first);
        out +=':';
        out += std::to_string(dist.second);
        out +=',';
    }

    return strdup(out.c_str());
  }

  char* get_branch_dists(){
    std::string out = "";

    for ( auto dist : branchDist){
            out += std::to_string(dist.first);
            out +=':';
            out += std::to_string(dist.second);
            out +=',';
    }

    return strdup(out.c_str());
  }

  char* get_takenness(){
    //Initialize histogram
    const uint32_t histogram_bins = 40;
    std::vector<uint64_t> histogram(histogram_bins, 0);

    //Iterate over outer map
    for(auto outer : pairCounts){

        //Calculate sum of inner map
        uint64_t inner_sum = 0;
        for(auto inner : outer.second){
            inner_sum += inner.second;
        }

        //Add takenness to histogram
        for(auto inner : outer.second){
            float takenness = float(inner.second) / float(inner_sum);
            int hist_idx = takenness * histogram_bins;
            histogram[hist_idx]++;
        }
    }

    //Dump histogram to string
    std::string out = "";

    for ( auto h : histogram){
            out += std::to_string(h);
            out +=',';
    }

    return strdup(out.c_str());
  }

  void clear_all(){
    trace.clear();

    //Address to seqnum distance
    seqDist.clear();
    seqDistCache.clear();

    //Address to effective seqnum distance
    effSeqDist.clear();
    effSeqDistCache.clear();

    //Address to effective seqnum distance
    global_branch_n = 0;
    branchDist.clear();
    branchDistCache.clear();

    //Pc -> Pc + count relation
    pairCache.clear();
    pairCounts.clear();

  }

  void clear_caches(){
    trace.clear();

    //Address to seqnum distance
    seqDistCache.clear();

    //Address to effective seqnum distance
    effSeqDistCache.clear();

    //Address to effective seqnum distance
    global_branch_n = 0;
    branchDistCache.clear();

    //Pc -> Pc + count relation
    pairCache.clear();

  }

  void calculate_statistics(char const* trace_path){
      boost::iostreams::filtering_istream infile;
      infile.push(boost::iostreams::zstd_decompressor());
      infile.push(boost::iostreams::file_source(trace_path));

    //Chunk loading and processing
    //while (infile.peek() != EOF){
    while (!infile.eof()){
        printf("Back to loading\n");
        load_trace(infile, 1000000);
        printf("Back to traversing\n");
        traverse();
        trace.clear();
    }

    // infile.close();
  }
}

int main(){
    //Load trace from file
    printf("Running main\n");
    calculate_statistics("/home/michal/Downloads/sha100k.csv.zst");
    printf("%s", get_branch_dists());
}