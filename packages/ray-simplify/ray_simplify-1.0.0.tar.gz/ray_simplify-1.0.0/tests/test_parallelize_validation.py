"""Tests for parallelize decorator validation."""

from unittest.mock import Mock, patch

import pytest

from ray_simplify.core import (
    DEFAULT_NUM_CPUS,
    parallelize,
)


class TestParallelizeValidation:
    """Test parallelize decorator validation."""

    def test_parallelize_invalid_max_concurrency(self):
        """Test parallelize raises ValueError for invalid max_concurrency."""
        with pytest.raises(ValueError, match="max_concurrency must be positive"):

            @parallelize(max_concurrency=0)
            def test_func():
                pass

        with pytest.raises(ValueError, match="max_concurrency must be positive"):

            @parallelize(max_concurrency=-1)
            def test_func():
                pass

    @patch("ray.is_initialized")
    @patch("ray.cluster_resources")
    def test_parallelize_cluster_resources_exception(
        self, mock_cluster_resources, mock_ray_initialized
    ):
        """Test parallelize handles cluster_resources exception."""
        mock_ray_initialized.return_value = True
        mock_cluster_resources.side_effect = Exception("Cluster error")

        mock_remote_func = Mock()
        mock_options_func = Mock()
        mock_options_func.remote.return_value = "result"
        mock_remote_func.options.return_value = mock_options_func

        with patch("ray.remote", return_value=mock_remote_func):

            @parallelize(max_concurrency=4)
            def test_func(x):
                return x

            test_func(5)
            # Should use DEFAULT_NUM_CPUS when cluster_resources fails
            expected_cpu_fraction = DEFAULT_NUM_CPUS / 4
            mock_remote_func.options.assert_called_once_with(
                num_cpus=expected_cpu_fraction
            )
