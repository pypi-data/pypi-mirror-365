"""Constants used throughout the Ray Simplify package.

This module defines constants used across different modules in the package
to ensure consistency and make configuration changes easier.
"""

# Default number of CPUs to allocate to Ray cluster
DEFAULT_NUM_CPUS = 8

# Default port for Ray cluster communication
DEFAULT_RAY_PORT = 10001

# Timeout for subprocess operations in seconds
SUBPROCESS_TIMEOUT_SECONDS = 30

# Default logging level for Ray operations
DEFAULT_LOG_LEVEL = "INFO"
