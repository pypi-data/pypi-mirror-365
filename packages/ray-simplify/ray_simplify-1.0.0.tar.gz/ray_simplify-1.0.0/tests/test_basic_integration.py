"""Tests for basic integration scenarios."""

from ray_simplify.core import parallelize


class TestBasicIntegration:
    """Test cases for basic integration scenarios."""

    def test_parallelize_decorator_function_signature_preservation(self):
        """Test that parallelize decorator preserves function signatures."""

        @parallelize()
        def function_with_args(a, b, c=10, *args, **kwargs):
            """Function with various argument types."""
            return a + b + c

        # Test that function metadata is preserved
        assert function_with_args.__name__ == "function_with_args"
        assert "Function with various argument types." in function_with_args.__doc__

        # Test that function works normally without Ray
        result = function_with_args(1, 2, c=3)
        assert result == 6

    def test_parallel_execution_without_ray_context(self):
        """Test that functions work normally when not in parallel context."""

        @parallelize()
        def simple_calculation(x):
            return x**2

        # Should work normally outside parallel context
        result = simple_calculation(5)
        assert result == 25
