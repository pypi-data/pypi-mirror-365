"""Decorator functions for Ray Simplify.

This module provides decorator functions that enhance regular functions
with parallel execution capabilities and error handling.
"""

import functools
import logging
from typing import Any, Callable, Optional

import ray

from .constants import DEFAULT_NUM_CPUS

log = logging.getLogger(__name__)


def parallelize(
    max_concurrency: Optional[int] = None,
) -> Callable[[Callable], Callable]:
    """Apply this decorator to any function, enabling it to be executed in parallel
    inside a parallel context.

    This decorator wraps a function to make it executable in parallel when Ray is
    initialized. When Ray is not available, the function executes normally.

    Args:
        max_concurrency: The maximum number of concurrent tasks. If None, uses all
            available CPUs. Must be positive if specified.

    Returns:
        A decorator function that wraps the target function for parallel execution.

    Raises:
        ValueError: If max_concurrency is not positive.

    Examples:
        Basic usage:
        >>> @parallelize()
        ... def calculate(x: int) -> int:
        ...     return x * x

        With concurrency limit:
        >>> @parallelize(max_concurrency=4)
        ... def process_data(data: str) -> str:
        ...     return data.upper()

        Using in parallel context:
        >>> with parallel() as ctx:
        ...     results = [calculate(i) for i in range(10)]
        ...     # Functions run in parallel, results are futures
    """
    if max_concurrency is not None and max_concurrency <= 0:
        raise ValueError("max_concurrency must be positive")

    def inner_parallelize(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check if running in parallel context
            if ray.is_initialized():
                log.debug(f"Executing {func.__name__} in parallel context")
                # Run the function in parallel and return the future
                ray_func = ray.remote(func)

                if max_concurrency is not None:
                    # Get current context's num_cpus or use default
                    current_cpus = DEFAULT_NUM_CPUS
                    try:
                        # Try to get actual cluster resources if available
                        cluster_resources = ray.cluster_resources()
                        current_cpus = int(
                            cluster_resources.get("CPU", DEFAULT_NUM_CPUS)
                        )
                    except Exception as e:
                        log.debug(
                            f"Could not get cluster resources, using default: {e}"
                        )

                    cpu_fraction = current_cpus / max_concurrency
                    return ray_func.options(num_cpus=cpu_fraction).remote(
                        *args, **kwargs
                    )
                return ray_func.remote(*args, **kwargs)

            # Not in parallel context, run function normally
            log.debug(f"Executing {func.__name__} in sequential context")
            return func(*args, **kwargs)

        # Mark the function as parallelizable
        wrapper.__parallelize__ = True
        return wrapper

    return inner_parallelize


def ignore_exception(func: Callable) -> Callable:
    """Decorator to ignore exceptions and log them at debug level.

    This decorator wraps a function to catch any exceptions it might raise,
    log them at debug level, and return None instead of propagating the exception.
    Useful for optional operations that shouldn't break the main flow.

    Args:
        func: The function to wrap.

    Returns:
        The wrapped function that catches and logs exceptions.

    Examples:
        >>> @ignore_exception
        ... def optional_operation(x):
        ...     if x < 0:
        ...         raise ValueError("Negative value")
        ...     return x * 2

        >>> result1 = optional_operation(5)   # Returns 10
        >>> result2 = optional_operation(-1)  # Returns None, logs error

        Preserves function metadata:
        >>> @ignore_exception
        ... def documented_func():
        ...     '''This function has documentation.'''
        ...     return "result"
        >>> print(documented_func.__name__)  # 'documented_func'
        >>> print(documented_func.__doc__)   # 'This function has documentation.'
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.debug(f"Error in {func.__name__}: {e}")
            return None

    return wrapper
