"""Custom exception classes for Ray Simplify.

This module defines custom exception classes for handling Ray-related errors
with specific error types for better error handling and debugging.
"""


class RayError(Exception):
    """Base exception for Ray-related errors.

    This is the base class for all Ray-related exceptions in the ray_simplify package.
    It provides a common base for catching all Ray-related errors.

    Examples:
        >>> try:
        ...     # Some Ray operation
        ...     pass
        ... except RayError as e:
        ...     print(f"Ray error occurred: {e}")
    """

    pass


class RayInitializationError(RayError):
    """Raised when Ray fails to initialize.

    This exception is raised when Ray cluster initialization fails, either
    locally or when connecting to a remote cluster.

    Examples:
        >>> try:
        ...     # Ray initialization
        ...     pass
        ... except RayInitializationError as e:
        ...     print(f"Failed to initialize Ray: {e}")
    """

    pass


class RayProcessError(RayError):
    """Raised when Ray subprocess operations fail.

    This exception is raised when subprocess operations for managing Ray
    clusters (start, stop, status) encounter errors.

    Examples:
        >>> try:
        ...     # Ray subprocess operation
        ...     pass
        ... except RayProcessError as e:
        ...     print(f"Ray process error: {e}")
    """

    pass
