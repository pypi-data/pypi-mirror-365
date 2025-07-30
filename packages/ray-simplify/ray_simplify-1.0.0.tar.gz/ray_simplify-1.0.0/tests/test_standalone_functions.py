"""Tests for standalone utility functions."""

from unittest.mock import Mock, patch

from ray_simplify.core import (
    ParallelContext,
    parallel,
    parallel_iter,
    parallel_map,
    parallel_shared,
    parallel_wait,
)


class TestStandaloneFunctions:
    """Test cases for standalone utility functions."""

    def test_parallel_function(self):
        """Test parallel function returns ParallelContext instance."""
        ctx = parallel()
        assert isinstance(ctx, ParallelContext)

    def test_parallel_function_with_kwargs(self):
        """Test parallel function with keyword arguments."""
        ctx = parallel(num_cpus=16, on_host="localhost")
        assert isinstance(ctx, ParallelContext)
        assert ctx._num_cpus == 16
        assert ctx._on_host == "localhost"

    @patch.object(ParallelContext, "_shared")
    def test_parallel_shared_function(self, mock_shared):
        """Test parallel_shared function."""
        mock_shared.return_value = "shared_ref"

        result = parallel_shared("test_data")

        mock_shared.assert_called_once_with("test_data")
        assert result == "shared_ref"

    @patch.object(ParallelContext, "_map")
    def test_parallel_map_function(self, mock_map):
        """Test parallel_map function."""
        mock_map.return_value = iter([1, 2, 3])

        def test_func(x):
            return x

        parallel_map(test_func, [1, 2, 3])

        mock_map.assert_called_once_with(test_func, [1, 2, 3])

    @patch.object(ParallelContext, "_iter")
    def test_parallel_iter_function(self, mock_iter):
        """Test parallel_iter function."""
        futures = [Mock(), Mock()]

        parallel_iter(futures)

        mock_iter.assert_called_once_with(futures)

    @patch.object(ParallelContext, "_wait")
    def test_parallel_wait_function(self, mock_wait):
        """Test parallel_wait function."""
        mock_wait.return_value = "result"

        future = Mock()
        result = parallel_wait(future)

        mock_wait.assert_called_once_with(future)
        assert result == "result"
