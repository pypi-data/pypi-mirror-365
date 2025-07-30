"""Module-level functions for Ray Simplify.

This module provides the main public API functions that users interact with
for parallel execution. These functions provide a convenient interface to
the underlying Ray functionality.
"""

from typing import Any, Callable, Generator, Iterator, List, Union

import ray

from .context import ParallelContext


def parallel(**kwargs: Any) -> ParallelContext:
    """Create a parallel context manager for Ray-based parallel execution.

    This is the main entry point for users to create a parallel execution context.
    It returns a ParallelContext that can be used as a context manager to
    automatically handle Ray initialization and cleanup.

    Args:
        **kwargs: Configuration options passed to ParallelContext:
            - num_cpus (int): Number of CPUs to allocate (default: 8)
            - on_host (str): Remote host address for distributed execution
            - log_level (str): Ray logging level (default: "INFO")
            - log_to_driver (bool): Whether to log to driver (default: True)

    Returns:
        A ParallelContext instance for use as a context manager.

    Raises:
        ValueError: If invalid configuration parameters are provided.

    Examples:
        Basic usage:
        >>> @parallelize()
        ... def calculate(x: int) -> int:
        ...     return x * x

        >>> with parallel() as ctx:
        ...     results = parallel_map(calculate, [1, 2, 3, 4])
        ...     for result in results:
        ...         print(result)

        With custom configuration:
        >>> with parallel(num_cpus=4, log_level="DEBUG") as ctx:
        ...     # Your parallel code here
        ...     pass

        Remote execution:
        >>> with parallel(on_host="192.168.1.100") as ctx:
        ...     # Execute on remote Ray cluster
        ...     pass
    """
    return ParallelContext(**kwargs)


def parallel_shared(data: Any) -> ray.ObjectRef:
    """Share data with Ray's object store for efficient access across workers.

    This function stores data in Ray's distributed object store, allowing
    multiple workers to access the same data efficiently without copying
    it to each worker.

    Args:
        data: The data to store in Ray's distributed object store.

    Returns:
        A Ray ObjectRef that can be passed to parallel functions to access the data.

    Raises:
        RayError: If Ray is not initialized or data storage fails.

    Examples:
        >>> with parallel() as ctx:
        ...     # Share large data once instead of copying to each worker
        ...     shared_data = parallel_shared([1, 2, 3, 4] * 1000)
        ...
        ...     @parallelize()
        ...     def process_shared(data_ref, multiplier):
        ...         data = ray.get(data_ref)  # Access shared data
        ...         return [x * multiplier for x in data]
        ...
        ...     results = parallel_map(process_shared, [shared_data] * 4, [1, 2, 3, 4])
    """
    return ParallelContext._shared(data)


def parallel_map(
    func: Callable, *args: Any, **kwargs: Any
) -> Union[Iterator, Generator]:
    """Execute a function in parallel across multiple arguments.

    This function applies a function to multiple sets of arguments in parallel.
    If the function is decorated with @parallelize() and Ray is initialized,
    it runs in parallel. Otherwise, it falls back to sequential execution.

    Args:
        func: The function to execute. Should be decorated with @parallelize() for
            parallel execution, otherwise runs sequentially.
        *args: Iterable arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        An iterator over the results. If the function is parallelizable and Ray is
        initialized, returns results as they become available. Otherwise returns
        a standard map iterator.

    Raises:
        ValueError: If func is not callable.
        RayError: If parallel execution fails.

    Examples:
        >>> @parallelize()
        ... def square(x: int) -> int:
        ...     return x * x

        >>> with parallel() as ctx:
        ...     results = parallel_map(square, [1, 2, 3, 4])
        ...     for result in results:
        ...         print(result)  # Results may arrive out of order

        With multiple argument lists:
        >>> @parallelize()
        ... def add(x: int, y: int) -> int:
        ...     return x + y

        >>> with parallel() as ctx:
        ...     results = parallel_map(add, [1, 2, 3], [4, 5, 6])
        ...     print(list(results))  # [5, 7, 9]
    """
    return ParallelContext._map(func, *args, **kwargs)


def parallel_iter(
    futures: List[Union[ray.ObjectRef, ray.ObjectRefGenerator]],
) -> Generator[Any, None, None]:
    """Iterate over Ray futures and yield results as they become available.

    This function takes a list of Ray futures and yields their results as they
    complete, allowing you to process results as soon as they're ready rather
    than waiting for all tasks to complete.

    Args:
        futures: A list of Ray ObjectRefs or ObjectRefGenerators from parallel function calls.

    Yields:
        Results from completed futures in the order they finish (not submission order).

    Raises:
        ValueError: If futures list is empty.
        RayError: If Ray is not initialized or iteration fails.

    Examples:
        >>> @parallelize()
        ... def slow_calculation(x: int) -> int:
        ...     import time
        ...     time.sleep(x)  # Simulate work
        ...     return x * x

        >>> with parallel() as ctx:
        ...     # Submit all tasks
        ...     futures = [slow_calculation(i) for i in [3, 1, 2, 4]]
        ...
        ...     # Get results as they complete (likely order: 1, 2, 3, 4)
        ...     for result in parallel_iter(futures):
        ...         print(f"Got result: {result}")
    """
    return ParallelContext._iter(futures)


def parallel_wait(future: ray.ObjectRef) -> Any:
    """Wait for a single Ray future to complete and return its result.

    This function blocks until the specified future completes and returns
    its result. Use this when you need to wait for a specific task to
    complete before proceeding.

    Args:
        future: A Ray ObjectRef from a parallel function call.

    Returns:
        The result of the completed computation.

    Raises:
        ValueError: If future is not a valid Ray ObjectRef.
        RayError: If Ray is not initialized or waiting fails.

    Examples:
        >>> @parallelize()
        ... def long_computation(n: int) -> int:
        ...     import time
        ...     time.sleep(2)
        ...     return sum(range(n))

        >>> with parallel() as ctx:
        ...     future = long_computation(100)
        ...     result = parallel_wait(future)
        ...     print(f"Computation result: {result}")
    """
    return ParallelContext._wait(future)
