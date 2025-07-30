"""Tests for the ignore_exception decorator."""

from ray_simplify.core import ignore_exception


class TestIgnoreExceptionDecorator:
    """Test cases for the ignore_exception decorator."""

    def test_ignore_exception_normal_execution(self):
        """Test ignore_exception decorator with normal function execution."""

        @ignore_exception
        def normal_function(x):
            return x * 2

        result = normal_function(5)
        assert result == 10

    def test_ignore_exception_with_exception(self):
        """Test ignore_exception decorator when function raises an exception."""

        @ignore_exception
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()
        assert result is None

    def test_ignore_exception_preserves_function_metadata(self):
        """Test that ignore_exception decorator preserves function metadata."""

        @ignore_exception
        def sample_function():
            """Sample docstring."""
            pass

        assert sample_function.__name__ == "sample_function"
        assert sample_function.__doc__ == "Sample docstring."
