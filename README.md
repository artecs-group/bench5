# bench5
A tool to automatically prepare, spawn and manage simulations for cache microarchitectural exploration.
Created to work in conjunction with [gem5-artecs](https://github.com/artecs-group/gem5-artecs).

The following benchmark suites are currently supported:
* [SPEC CPU2006](https://www.spec.org/cpu2006/)
* [SPEC CPU2017](https://www.spec.org/cpu2017/)

The following operations are currently supported:
* Benchmarks simulation (SE mode)
  * `-f` : Standard execution
  * `-x` : From [SimPoint](https://cseweb.ucsd.edu/~calder/simpoint/)-based checkpoint
  * `-r` : From [Elastic Trace](https://www.gem5.org/documentation/general_docs/cpu_models/TraceCPU)
* `-b` : Basic Block Vectors (BBV) generation
  * using gem5 or [Valgrind](https://valgrind.org/docs/manual/bbv-manual.html)
* `-s` : Simulation Points extraction
  * using [SimPoint](https://cseweb.ucsd.edu/~calder/simpoint/)
* `-c` : Checkpoints creation from Simulation Points
* `-t` : [Elastic Traces](https://www.gem5.org/documentation/general_docs/cpu_models/TraceCPU) generation

## Requirements ##
This script is compatible with both Python 2 and Python 3. Make sure you install `subprocess32` if you want to use the former.

## Instructions ##
CPU and cache parameters have to be set in the `simparams.py` file. Many other options can be passed as command-line arguments.
Execute with option `-h` to show the help.
