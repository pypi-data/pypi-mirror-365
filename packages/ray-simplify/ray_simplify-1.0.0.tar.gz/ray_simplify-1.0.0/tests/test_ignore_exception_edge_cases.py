"""Tests for ignore_exception decorator edge cases."""

from ray_simplify.core import ignore_exception


class TestIgnoreExceptionEdgeCases:
    """Test ignore_exception decorator edge cases."""

    def test_ignore_exception_with_args_kwargs(self):
        """Test ignore_exception with function that takes args and kwargs."""

        @ignore_exception
        def func_with_args(a, b, c=10, *args, **kwargs):
            if a == "error":
                raise ValueError("Test error")
            return a + b + c + sum(args) + sum(kwargs.values())

        # Normal execution
        result = func_with_args(1, 2, 3, 4, 5, x=6, y=7)
        assert result == 28  # 1+2+3+4+5+6+7

        # Exception case
        result = func_with_args("error", 2)
        assert result is None

    def test_ignore_exception_preserves_docstring(self):
        """Test ignore_exception preserves function docstring."""

        @ignore_exception
        def documented_func():
            """This is a documented function."""
            return "result"

        assert documented_func.__doc__ == "This is a documented function."
