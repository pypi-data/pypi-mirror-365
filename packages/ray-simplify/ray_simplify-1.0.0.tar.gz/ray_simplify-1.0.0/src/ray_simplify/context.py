"""Parallel context manager for Ray execution.

This module provides the ParallelContext class which serves as a context manager
for Ray-based parallel execution, handling initialization, cleanup, and providing
utility methods for parallel operations.
"""

import logging
from typing import Any, Callable, Generator, Iterator, List, Optional, Union

import ray

from .constants import DEFAULT_LOG_LEVEL, DEFAULT_NUM_CPUS, DEFAULT_RAY_PORT
from .exceptions import RayInitializationError
from .executor import RayExecutor
from .process_manager import RayProcessManager

log = logging.getLogger(__name__)


class ParallelContext:
    """A context manager for parallel execution using Ray.

    This class provides a context manager to facilitate parallel execution of functions
    using Ray. It handles the initialization and shutdown of Ray, and provides utility
    methods for parallel execution and data sharing.

    The context manager can work with local Ray clusters (starting/stopping as needed)
    or connect to remote Ray clusters.

    Attributes:
        _num_cpus: Number of CPUs to allocate to Ray.
        _on_host: Remote host address for Ray cluster.
        _log_level: Logging level for Ray.
        _log_to_driver: Whether to log to driver.
        _process_manager: Manages Ray subprocess operations.
        _is_self_hosted: Whether this context started its own Ray cluster.

    Examples:
        Basic local usage:
        >>> with ParallelContext() as ctx:
        ...     # Ray is automatically started and stopped
        ...     shared_data = ctx._shared([1, 2, 3, 4])
        ...     # Perform parallel operations

        Remote cluster usage:
        >>> with ParallelContext(on_host="192.168.1.100") as ctx:
        ...     # Connect to existing Ray cluster
        ...     # Perform parallel operations

        Custom configuration:
        >>> with ParallelContext(num_cpus=16, log_level="DEBUG") as ctx:
        ...     # Use custom settings
        ...     # Perform parallel operations
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the parallel context object.

        Args:
            **kwargs: Configuration options:
                - num_cpus (int): Number of CPUs (default: 8)
                - on_host (str): Remote host address (default: None)
                - log_level (str): Ray logging level (default: "INFO")
                - log_to_driver (bool): Log to driver (default: True)

        Raises:
            ValueError: If invalid configuration parameters are provided.

        Examples:
            >>> ctx = ParallelContext()  # Default settings
            >>> ctx = ParallelContext(num_cpus=4, log_level="DEBUG")
            >>> ctx = ParallelContext(on_host="10.0.0.1")  # Remote cluster
        """
        self._num_cpus = kwargs.get("num_cpus", DEFAULT_NUM_CPUS)
        self._on_host = kwargs.get("on_host", None)
        self._log_level = kwargs.get("log_level", DEFAULT_LOG_LEVEL)
        self._log_to_driver = kwargs.get("log_to_driver", True)

        # Validate inputs
        if self._num_cpus <= 0:
            raise ValueError("num_cpus must be positive")

        if self._on_host is not None and not isinstance(self._on_host, str):
            raise ValueError("on_host must be a string")

        if self._log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("log_level must be a valid logging level")

        self._process_manager = RayProcessManager(self._num_cpus)
        self._is_self_hosted = False

    def __enter__(self) -> "ParallelContext":
        """Enter the parallel context and initialize Ray.

        Ensures that Ray is properly initialized and running, either on a remote host
        or locally, before entering the context of the with statement.

        Returns:
            The ParallelContext instance.

        Raises:
            RayInitializationError: If Ray fails to initialize.

        Examples:
            >>> with ParallelContext() as ctx:
            ...     # Ray is now initialized and ready
            ...     print("Ray is ready for parallel execution")
        """
        try:
            # Connect to remote Ray cluster if specified
            if self._on_host is not None:
                log.info(f"Connecting to Ray cluster at {self._on_host}")
                ray.init(
                    address=f"ray://{self._on_host}:{DEFAULT_RAY_PORT}",
                    log_to_driver=self._log_to_driver,
                    runtime_env={"working_dir": ".", "excludes": [".git/*"]},
                    logging_level=self._log_level,
                )
                log.info("Successfully connected to remote Ray cluster")
                return self

            # Check if Ray is already running locally
            ray_status = self._process_manager.get_ray_status()
            self._is_self_hosted = ray_status == "offline"

            # Start Ray cluster if needed
            if self._is_self_hosted:
                self._process_manager.start_ray()

            # Initialize Ray client if not already done
            if not ray.is_initialized():
                log.info("Initializing Ray client")
                ray.init(
                    log_to_driver=self._log_to_driver,
                    logging_level=self._log_level,
                    local_mode=False,
                    include_dashboard=False,
                    configure_logging=False,
                )
                log.info("Ray client initialized successfully")

            return self

        except Exception as e:
            # Cleanup on failure
            if self._is_self_hosted:
                try:
                    self._process_manager.stop_ray()
                except Exception as cleanup_error:
                    log.error(f"Error during cleanup: {cleanup_error}")

            raise RayInitializationError(
                f"Failed to initialize Ray context: {e}"
            ) from e

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> None:
        """Exit the parallel context and cleanup Ray resources.

        Ensures that Ray is properly shut down and any resources allocated by Ray
        are cleaned up when the context is exited.

        Args:
            exc_type: Exception type if an exception occurred.
            exc_val: Exception value if an exception occurred.
            exc_tb: Exception traceback if an exception occurred.

        Examples:
            >>> with ParallelContext() as ctx:
            ...     # Do parallel work
            ...     pass
            # Ray is automatically cleaned up here
        """
        try:
            # Shutdown Ray client
            if ray.is_initialized():
                log.info("Shutting down Ray client")
                ray.shutdown(_exiting_interpreter=True)
                log.info("Ray client shutdown complete")

            # Stop Ray cluster if we started it
            if self._is_self_hosted:
                self._process_manager.stop_ray()

        except Exception as e:
            log.error(f"Error during Ray shutdown: {e}")
            # Don't raise exceptions in __exit__ as it can mask original exceptions

    @staticmethod
    def _shared(data: Any) -> ray.ObjectRef:
        """Share data with Ray's object store.

        Args:
            data: The data to store.

        Returns:
            Ray ObjectRef for the stored data.

        Examples:
            >>> with ParallelContext() as ctx:
            ...     shared_ref = ctx._shared([1, 2, 3, 4])
            ...     # Use shared_ref in parallel functions
        """
        return RayExecutor.shared(data)

    @staticmethod
    def _map(func: Callable, *args: Any, **kwargs: Any) -> Union[Iterator, Generator]:
        """Run a function in parallel with the given data.

        Args:
            func: The function to execute.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments.

        Returns:
            Iterator over results.

        Examples:
            >>> with ParallelContext() as ctx:
            ...     @parallelize()
            ...     def square(x):
            ...         return x * x
            ...     results = ctx._map(square, [1, 2, 3, 4])
        """
        return RayExecutor.map_parallel(func, *args, **kwargs)

    @staticmethod
    def _iter(
        futures: List[Union[ray.ObjectRef, ray.ObjectRefGenerator]],
    ) -> Generator[Any, None, None]:
        """Iterate over futures and yield results as they become available.

        Args:
            futures: A list of Ray object references or generators.

        Yields:
            The result of each completed future.

        Examples:
            >>> with ParallelContext() as ctx:
            ...     futures = [some_parallel_function(i) for i in range(10)]
            ...     for result in ctx._iter(futures):
            ...         print(f"Got result: {result}")
        """
        return RayExecutor.iter_futures(futures)

    @staticmethod
    def _wait(future: ray.ObjectRef) -> Any:
        """Wait for a future to complete and return its result.

        Args:
            future: The Ray ObjectRef to wait for.

        Returns:
            The result of the completed future.

        Examples:
            >>> with ParallelContext() as ctx:
            ...     future = some_parallel_function(42)
            ...     result = ctx._wait(future)
            ...     print(f"Result: {result}")
        """
        return RayExecutor.wait_for_result(future)
