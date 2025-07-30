"""Tests for the parallelize decorator."""

from unittest.mock import Mock, patch

from ray_simplify.core import parallelize


class TestParallelizeDecorator:
    """Test cases for the parallelize decorator."""

    def test_parallelize_decorator_basic_functionality(self):
        """Test that parallelize decorator properly wraps a function."""

        @parallelize()
        def sample_function(x):
            return x * 2

        assert hasattr(sample_function, "__parallelize__")
        assert sample_function.__parallelize__ is True
        assert sample_function.__name__ == "sample_function"

    def test_parallelize_with_max_concurrency(self):
        """Test parallelize decorator with max_concurrency parameter."""

        @parallelize(max_concurrency=4)
        def sample_function(x):
            return x * 2

        assert hasattr(sample_function, "__parallelize__")
        assert sample_function.__parallelize__ is True

    @patch("ray.is_initialized")
    def test_parallelize_without_ray_context(self, mock_ray_initialized):
        """Test parallelize decorator when Ray is not initialized."""
        mock_ray_initialized.return_value = False

        @parallelize()
        def sample_function(x):
            return x * 2

        result = sample_function(5)
        assert result == 10

    @patch("ray.remote")
    @patch("ray.is_initialized")
    def test_parallelize_with_ray_context(self, mock_ray_initialized, mock_ray_remote):
        """Test parallelize decorator when Ray is initialized."""
        mock_ray_initialized.return_value = True
        mock_remote_func = Mock()
        mock_remote_func.remote.return_value = "future_result"
        mock_ray_remote.return_value = mock_remote_func

        @parallelize()
        def sample_function(x):
            return x * 2

        result = sample_function(5)
        mock_ray_remote.assert_called_once_with(sample_function.__wrapped__)
        mock_remote_func.remote.assert_called_once_with(5)
        assert result == "future_result"

    @patch("ray.remote")
    @patch("ray.is_initialized")
    @patch("ray.cluster_resources")
    def test_parallelize_with_max_concurrency_and_ray(
        self, mock_cluster_resources, mock_ray_initialized, mock_ray_remote
    ):
        """Test parallelize decorator with max_concurrency when Ray is initialized."""
        mock_ray_initialized.return_value = True
        mock_cluster_resources.return_value = {"CPU": 8}
        mock_remote_func = Mock()
        mock_options_func = Mock()
        mock_options_func.remote.return_value = "future_result"
        mock_remote_func.options.return_value = mock_options_func
        mock_ray_remote.return_value = mock_remote_func

        @parallelize(max_concurrency=4)
        def sample_function(x):
            return x * 2

        result = sample_function(5)
        mock_ray_remote.assert_called_once_with(sample_function.__wrapped__)
        mock_remote_func.options.assert_called_once_with(
            num_cpus=2.0
        )  # 8 CPUs / 4 max_concurrency
        mock_options_func.remote.assert_called_once_with(5)
        assert result == "future_result"
