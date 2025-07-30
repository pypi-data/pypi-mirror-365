"""Core module for Ray Simplify - Central import aggregation.

This module aggregates imports from all ray_simplify sub-modules to provide
a single import point for tests and backward compatibility.
"""

# Import constants
from .constants import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_NUM_CPUS,
    DEFAULT_RAY_PORT,
    SUBPROCESS_TIMEOUT_SECONDS,
)

# Import context
from .context import ParallelContext

# Import decorators
from .decorators import ignore_exception, parallelize

# Import exceptions
from .exceptions import (
    RayError,
    RayInitializationError,
    RayProcessError,
)

# Import executor
from .executor import RayExecutor

# Import functions
from .functions import (
    parallel,
    parallel_iter,
    parallel_map,
    parallel_shared,
    parallel_wait,
)

# Import process manager
from .process_manager import RayProcessManager

# Export all for backward compatibility
__all__ = [
    # Constants
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_NUM_CPUS",
    "DEFAULT_RAY_PORT",
    "SUBPROCESS_TIMEOUT_SECONDS",
    # Exceptions
    "RayError",
    "RayInitializationError",
    "RayProcessError",
    # Classes
    "RayProcessManager",
    "RayExecutor",
    "ParallelContext",
    # Decorators
    "parallelize",
    "ignore_exception",
    # Functions
    "parallel",
    "parallel_iter",
    "parallel_map",
    "parallel_shared",
    "parallel_wait",
]
