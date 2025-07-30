"""Simplify use of ray

This package demonstrates modern Python packaging practices with integrated
tooling for code quality, testing, and documentation.
"""

__version__ = "1.0.0"

"""
## Ray Simplify Core Module

**Purpose**:

* Simplifies parallel execution of functions using the Ray distributed computing framework.
* Automatically manages Ray initialization and termination.

**Functionality**:

* **Initialization**: Starts the Ray distributed system upon entering the context manager.
* **Parallel Execution**: Enables functions within the context to be executed in parallel across multiple Ray workers.
* **Termination**: Shuts down the Ray system when the context manager exits, releasing resources.

**Benefits**:

* **Efficiency**: Leverages Ray's distributed capabilities for performance gains.
* **Simplicity**: Provides a convenient way to parallelize code without explicit Ray management.
* **Resource Management**: Ensures proper cleanup of Ray resources.
* **Error Handling**: Comprehensive error handling with specific exception types.
* **Type Safety**: Full type annotations for better IDE support and code reliability.

**Functions**:

- parallelize(): Decorator to enable parallelizing.
- parallel(): Context manager to run the function in parallel.
- parallel_map(): Run a function in parallel with the data.
- parallel_shared(): Share data with Ray.
- parallel_iter(): Iterate over futures as results become available.
- parallel_wait(): Wait for a single future to complete.

**Exception Classes**:

- RayError: Base exception for Ray-related errors.
- RayInitializationError: Raised when Ray fails to initialize.
- RayProcessError: Raised when Ray subprocess operations fail.

This module now serves as a central import point for all ray_simplify functionality.
The actual implementations have been moved to separate modules for better organization:

- exceptions.py: Custom exception classes
- constants.py: Package constants
- process_manager.py: Ray process management
- executor.py: Ray execution operations
- decorators.py: Function decorators
- context.py: Parallel context manager
- functions.py: Public API functions
"""
