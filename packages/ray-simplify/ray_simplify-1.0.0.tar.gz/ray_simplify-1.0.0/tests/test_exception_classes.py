"""Tests for custom exception classes."""

from ray_simplify.core import (
    RayError,
    RayInitializationError,
    RayProcessError,
)


class TestExceptionClasses:
    """Test custom exception classes."""

    def test_ray_error_inheritance(self):
        """Test RayError is properly defined."""
        error = RayError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_ray_initialization_error_inheritance(self):
        """Test RayInitializationError is properly defined."""
        error = RayInitializationError("Init error")
        assert isinstance(error, RayError)
        assert isinstance(error, Exception)
        assert str(error) == "Init error"

    def test_ray_process_error_inheritance(self):
        """Test RayProcessError is properly defined."""
        error = RayProcessError("Process error")
        assert isinstance(error, RayError)
        assert isinstance(error, Exception)
        assert str(error) == "Process error"
