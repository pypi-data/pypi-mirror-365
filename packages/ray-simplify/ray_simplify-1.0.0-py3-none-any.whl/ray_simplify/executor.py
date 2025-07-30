"""Ray execution operations.

This module provides the RayExecutor class which handles Ray execution
operations including data sharing, parallel mapping, future iteration,
and result waiting.
"""

import logging
from typing import Any, Callable, Generator, Iterator, List, Union

import ray

from .exceptions import RayError

log = logging.getLogger(__name__)


class RayExecutor:
    """Handles Ray execution operations.

    This class provides static methods for common Ray operations such as
    sharing data in Ray's object store, mapping functions in parallel,
    iterating over futures, and waiting for results.

    All methods are static as they operate on Ray's global state and
    don't require instance-specific data.

    Examples:
        >>> # Share data in Ray's object store
        >>> shared_data = RayExecutor.shared([1, 2, 3, 4])
        >>>
        >>> # Map a function in parallel
        >>> @parallelize()
        ... def square(x):
        ...     return x * x
        >>> results = RayExecutor.map_parallel(square, [1, 2, 3, 4])
    """

    @staticmethod
    def shared(data: Any) -> ray.ObjectRef:
        """Share data with Ray's object store.

        Args:
            data: The data to store in Ray's object store.

        Returns:
            A Ray ObjectRef pointing to the stored data.

        Raises:
            RayError: If Ray is not initialized or data storage fails.

        Examples:
            >>> data = [1, 2, 3, 4] * 1000  # Large data
            >>> shared_ref = RayExecutor.shared(data)
            >>> # Pass shared_ref to parallel functions instead of data
        """
        if not ray.is_initialized():
            raise RayError("Ray is not initialized. Use within a parallel context.")

        try:
            return ray.put(data)
        except Exception as e:
            raise RayError(f"Failed to store data in Ray object store: {e}") from e

    @staticmethod
    def map_parallel(
        func: Callable, *args: Any, **kwargs: Any
    ) -> Union[Iterator, Generator]:
        """Run a function in parallel with the given data.

        Args:
            func: The function to execute. Should be decorated with @parallelize()
                for parallel execution.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            Iterator over results if function is parallelizable and Ray is
            initialized, else regular map result.

        Raises:
            ValueError: If func is not callable.

        Examples:
            >>> @parallelize()
            ... def process(x, multiplier=2):
            ...     return x * multiplier
            >>>
            >>> results = RayExecutor.map_parallel(process, [1, 2, 3], multiplier=3)
            >>> print(list(results))  # [3, 6, 9]
        """
        if not callable(func):
            raise ValueError("func must be callable")

        # If func is decorated with parallelize, run its parallel iterable results
        if getattr(func, "__parallelize__", False):
            if not ray.is_initialized():
                log.warning(
                    "Function is parallelizable but Ray not initialized, running sequentially"
                )
                return map(func, *args, **kwargs)

            futures = [*map(func, *args, **kwargs)]
            return RayExecutor.iter_futures(futures)
        else:
            return map(func, *args, **kwargs)

    @staticmethod
    def iter_futures(
        futures: List[Union[ray.ObjectRef, ray.ObjectRefGenerator]],
    ) -> Generator[Any, None, None]:
        """Iterate over futures and yield results as they become available.

        Args:
            futures: A list of Ray object references or generators.

        Yields:
            The result of each completed future in the order they complete
            (not necessarily the order they were submitted).

        Raises:
            ValueError: If futures list is empty.
            RayError: If Ray is not initialized or Ray operations fail.

        Examples:
            >>> @parallelize()
            ... def slow_task(x, delay):
            ...     import time
            ...     time.sleep(delay)
            ...     return x * x
            >>>
            >>> # Submit tasks with different delays
            >>> futures = [slow_task(i, delay) for i, delay in [(1, 3), (2, 1), (3, 2)]]
            >>>
            >>> # Get results as they complete (likely order: 2, 3, 1)
            >>> for result in RayExecutor.iter_futures(futures):
            ...     print(f"Completed: {result}")
        """
        if not futures:
            raise ValueError("futures list cannot be empty")

        if not ray.is_initialized():
            raise RayError("Ray is not initialized")

        try:
            futures_copy = list(futures)  # Make a copy to avoid modifying input
            while futures_copy:
                done, futures_copy = ray.wait(futures_copy, num_returns=1)
                for done_future in done:
                    yield ray.get(done_future)
        except Exception as e:
            raise RayError(f"Error iterating over futures: {e}") from e

    @staticmethod
    def wait_for_result(future: ray.ObjectRef) -> Any:
        """Wait for a future to complete and return its result.

        Args:
            future: The Ray ObjectRef to wait for.

        Returns:
            The result of the completed future.

        Raises:
            ValueError: If future is not a valid ObjectRef.
            RayError: If Ray is not initialized or Ray operations fail.

        Examples:
            >>> @parallelize()
            ... def long_computation(n):
            ...     return sum(range(n))
            >>>
            >>> future = long_computation(1000000)
            >>> result = RayExecutor.wait_for_result(future)
            >>> print(f"Sum: {result}")
        """
        if not isinstance(future, ray.ObjectRef):
            raise ValueError("future must be a Ray ObjectRef")

        if not ray.is_initialized():
            raise RayError("Ray is not initialized")

        try:
            return ray.get(future)
        except Exception as e:
            raise RayError(f"Error getting result from future: {e}") from e
