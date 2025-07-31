.. _function_approximation:

========================================
The Function Approximation Toy Benchmark
========================================

| **Task:** approximate a function at timestep t in each of one or multiple dimensions
| **Cost:** distance between prediction and function
| **Number of hyperparameters to control:** user specified starting at one integer with no fixed upper limit
| **State Information:** Remaining budget, instance descriptions for each dimension (inflection point and slope), last action for each dimension
| **Noise Level:** None
| **Instance space:** one simple function (constant, sigmoid, logarithmic, quadratic, polynomial) per dimension. Sampling notebook and example datasets in repository.

This benchmark is not built on top of an algorithm, but is simply a function approximation task.
In each step until the cutoff, the DAC controller predicts one y-value for a given function
curve per task dimension.
The predictions are can be configured to be discrete, in which case there is some distance between the true
function value and the best possible prediction. This distance is used as a cost function. If multiple
task dimensions are used, the total cost is computed by multiplying the costs of all dimensions.
Furthermore, it is possible to assign different importance weights to each dimension, mirroring hyperparameter importances.

The benchmark is very cheap to run and the instances can be sampled and shaped easily.
Therefore it's a good starting point for any new DAC method or to gain specific insights for
which fine control over the instance distribution is required.

*The Sigmoid benchmark was constructed by Biedenkapp et al. for the paper `"Dynamic Algorithm Configuration: Foundation of a New Meta-Algorithmic Framework" <https://www.tnt.uni-hannover.de/papers/data/1432/20-ECAI-DAC.pdf>`_ at ECAI 2020* and later extended to include multiple function classes and importance weights.


.. automodule:: dacbench.benchmarks.function_approximation_benchmark
    :members:
    :show-inheritance:

.. automodule:: dacbench.envs.function_approximation
    :members:
    :show-inheritance: