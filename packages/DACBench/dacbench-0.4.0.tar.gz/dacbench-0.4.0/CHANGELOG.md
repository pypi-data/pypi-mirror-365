# 0.3.0

### Instance Specification
Instances for most benchmarks now have a dataclass Type instead of being a simple list. Additionally, the corresponding datasets are saved as proper csv files with headers now. This should make anything relating to instances much more convenient for the user. The benchmarks in question are:
- CMA-ES
- SGD
- Luby
- ToySGD
- Function Approximation

### Unifying CMA-ES Versions
Instead of having two different versions of CMA-ES, we now have a single environment which covers both step size adaption and algorithm variant selection of CMA-ES (formerly ModCMA). By changing the configuration space, the user can select which hyperparameters to adapt. This change includes a switch to the newer "ioh" package, meaning an increased amount of target functions could be interfaced in principle. Anything outside of BBOB will need to be loaded separately from the "read_instance_set" function of the benchmark, however.

### Unifying Function Approximation Tasks
To reduce the number of separate classes to maintain for simple function approximation, the Sigmoid variations and the Geometric environment have been fused into the FunctionApproximation Benchmark. There are several options for functions to approximate, as in Sigmoid it is possible to use a discrete space and you can add importance weights for the dimensions. The "get_benchmark" method will still provide the original Sigmoid configurations. Apart from that, this new environment should provide all functionality of the previous environments, just with a simpler path to getting there.

### Re-implementing SGD Benchmark
The original SGD benchmark was complex and error prone, lacking important features like compatibility with torchhub. Therefore this has been re-implemented, mostly based on the existing competition version. The code is simpler now and compatible with a larger selection of models and optimizers.

### Deprecating FastDownward
The FastDownward version compatible with the benchmark cannot be used with any Ubuntu version after 16.x - which is fairly old by now. For reference, it is not possible to even build a container for this version of FastDownward on th GitHub servers. Since there is no option to update the planner version without updating the environment and this is tied to significant domain knowledge, FastDownward will now be deprecated. This means there is no testing, the benchmark will not be updated and it will not be listed as an official benchmark any longer. If someone is familiar enough with FastDownward to facilitate an update, please notify us, we'd love to continue this benchmark!

### Updating Instance Sets
Most instance sets have been updated due to the instance specification change. The Sigmoid ones have been preserved, the rest has been updated. Sampling options for all benchmarks are included in the "instance_set" directory, however.

### Logger Update
The logs have been a bit hard to read & work with. We flattened them by removing timestamps, hopefully making them easier to work with.

### Dependency Upgrades
The dependencies have been upgraded to their current highest possible version.

### Simplify Examples
Some examples had a lot of extra dependencies. We removed many of these for now - this means less explicit RL examples, but if you want to use an RL library, DACBench will plug in like any other env, so you should read their documentation anyway.

### Including Instance Files in PyPI 
There was a persistent configuration mistake which prevented the instance sets to be included in the PyPI installation - this should now be fixed and all instances sets from the repository come with the PyPI package.

# 0.2.0

### Interface Update
The main change in this version is going from OpenAI's gym to the newer gymnasium version. The outward change is slight, but this interface is now **incompatible with version 0.1.0**. 
To adapt to this version, you'll mainly have to replace instances of 'done' for termination with two variables: 'terminated' indication algorithm termination and 'truncated' indicating a timeout.
Combined they're equal to the old 'done'.
Additonally, the default version of the environments is now available in the gym registry.

### Multi-Agent / Round Robin Control Option
We added more options for controlling several hyperparameters at once. Using the PettingZoo API, users can now select which hyperparameters to control and use a typical Multi-Agent RL interface to do it.
This should provide more freedom in how to solve the problem of scaling up to multiple hyperparameters.

### Package Versions
We updated all our dependencies for this release. Please note that this will likely influence benchmark behaviour, so **do not** directly compare performance of version 0.2.0 with 0.1.0!

### Benchmark Changes
The OneLL benchmark is not the Theory benchmark with a similar goal and setup, but a different base problem. 
For versioning reasons, we removed ModEA, the same problem should be covered by ModCMA.
We also add a toy benchmark for higher dimensional spaces, the Geometric Benchmark.

### Switches Docs to GitHub.io
The documentation is now hosted on GitHub.io instead of Read the Docs for versioning reasons. The old version should still be accessible, however.


# 0.1.0
### Added Benchmarks
New benchmarks include the ModCMA IOHExperimenter version of ModEA, the OneLL EA benchmark and a toy version of controlling SGD.

### Singularity Containers
For added reproducibility, we provide Singularity recipes for each benchmark. This way they can be run in containers.

## ConfigSpace Integration
Search Spaces can now be defined via ConfigSpace and are then automatically converted to gym spaces. 
This should make it easier to recover whcih actions correspond to which hyperparameters.

# 0.0.1
Initial Version