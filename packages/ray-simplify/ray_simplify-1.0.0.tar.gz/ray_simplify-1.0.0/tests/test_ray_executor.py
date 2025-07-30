"""Tests for RayExecutor class."""

from unittest.mock import Mock, patch

import pytest
import ray

from ray_simplify.core import (
    RayError,
    RayExecutor,
    parallelize,
)


class TestRayExecutor:
    """Test RayExecutor class."""

    @patch("ray.is_initialized")
    def test_shared_ray_not_initialized(self, mock_ray_initialized):
        """Test shared raises RayError when Ray not initialized."""
        mock_ray_initialized.return_value = False

        with pytest.raises(RayError, match="Ray is not initialized"):
            RayExecutor.shared("test_data")

    @patch("ray.put")
    @patch("ray.is_initialized")
    def test_shared_success(self, mock_ray_initialized, mock_ray_put):
        """Test shared succeeds when Ray is initialized."""
        mock_ray_initialized.return_value = True
        mock_ray_put.return_value = "object_ref"

        result = RayExecutor.shared("test_data")

        assert result == "object_ref"
        mock_ray_put.assert_called_once_with("test_data")

    @patch("ray.put")
    @patch("ray.is_initialized")
    def test_shared_ray_error(self, mock_ray_initialized, mock_ray_put):
        """Test shared raises RayError when ray.put fails."""
        mock_ray_initialized.return_value = True
        mock_ray_put.side_effect = Exception("Ray put failed")

        with pytest.raises(RayError, match="Failed to store data in Ray object store"):
            RayExecutor.shared("test_data")

    def test_map_parallel_non_callable(self):
        """Test map_parallel raises ValueError for non-callable."""
        with pytest.raises(ValueError, match="func must be callable"):
            RayExecutor.map_parallel("not_callable")

    def test_map_parallel_non_parallelizable(self):
        """Test map_parallel with non-parallelizable function."""

        def normal_func(x):
            return x * 2

        result = RayExecutor.map_parallel(normal_func, [1, 2, 3])
        assert list(result) == [2, 4, 6]

    @patch("ray.is_initialized")
    def test_map_parallel_parallelizable_ray_not_initialized(
        self, mock_ray_initialized
    ):
        """Test map_parallel with parallelizable function but Ray not initialized."""
        mock_ray_initialized.return_value = False

        @parallelize()
        def parallel_func(x):
            return x * 2

        result = RayExecutor.map_parallel(parallel_func, [1, 2, 3])
        assert list(result) == [2, 4, 6]

    @patch("ray.is_initialized")
    @patch("ray.remote")
    def test_map_parallel_parallelizable_ray_initialized(
        self, mock_ray_remote, mock_ray_initialized
    ):
        """Test map_parallel with parallelizable function and Ray initialized."""
        mock_ray_initialized.return_value = True

        # Mock ray.remote to return a mock function that returns futures
        mock_remote_func = Mock()
        mock_remote_func.remote.side_effect = ["future1", "future2", "future3"]
        mock_ray_remote.return_value = mock_remote_func

        @parallelize()
        def parallel_func(x):
            return x * 2

        with patch.object(
            RayExecutor, "iter_futures", return_value=iter([2, 4, 6])
        ) as mock_iter:
            result = RayExecutor.map_parallel(parallel_func, [1, 2, 3])
            result_list = list(result)

            # Verify that ray.remote was called and iter_futures was called with the futures
            assert mock_ray_remote.call_count >= 1
            mock_iter.assert_called_once_with(["future1", "future2", "future3"])
            assert result_list == [2, 4, 6]

    def test_iter_futures_empty_list(self):
        """Test iter_futures raises ValueError for empty list."""
        with pytest.raises(ValueError, match="futures list cannot be empty"):
            list(RayExecutor.iter_futures([]))

    @patch("ray.is_initialized")
    def test_iter_futures_ray_not_initialized(self, mock_ray_initialized):
        """Test iter_futures raises RayError when Ray not initialized."""
        mock_ray_initialized.return_value = False

        with pytest.raises(RayError, match="Ray is not initialized"):
            list(RayExecutor.iter_futures(["future1"]))

    @patch("ray.get")
    @patch("ray.wait")
    @patch("ray.is_initialized")
    def test_iter_futures_success(
        self, mock_ray_initialized, mock_ray_wait, mock_ray_get
    ):
        """Test iter_futures succeeds."""
        mock_ray_initialized.return_value = True

        # Setup the wait/get cycle
        futures = ["future1", "future2"]
        mock_ray_wait.side_effect = [
            (["future1"], ["future2"]),
            (["future2"], []),
        ]
        mock_ray_get.side_effect = ["result1", "result2"]

        results = list(RayExecutor.iter_futures(futures))

        assert results == ["result1", "result2"]
        assert mock_ray_wait.call_count == 2
        assert mock_ray_get.call_count == 2

    @patch("ray.wait")
    @patch("ray.is_initialized")
    def test_iter_futures_ray_error(self, mock_ray_initialized, mock_ray_wait):
        """Test iter_futures raises RayError when ray operations fail."""
        mock_ray_initialized.return_value = True
        mock_ray_wait.side_effect = Exception("Ray wait failed")

        with pytest.raises(RayError, match="Error iterating over futures"):
            list(RayExecutor.iter_futures(["future1"]))

    def test_wait_for_result_invalid_future(self):
        """Test wait_for_result raises ValueError for invalid future."""
        with pytest.raises(ValueError, match="future must be a Ray ObjectRef"):
            RayExecutor.wait_for_result("not_a_future")

    @patch("ray.is_initialized")
    def test_wait_for_result_ray_not_initialized(self, mock_ray_initialized):
        """Test wait_for_result raises RayError when Ray not initialized."""
        mock_ray_initialized.return_value = False

        # Create a mock ObjectRef
        mock_future = Mock(spec=ray.ObjectRef)

        with pytest.raises(RayError, match="Ray is not initialized"):
            RayExecutor.wait_for_result(mock_future)

    @patch("ray.get")
    @patch("ray.is_initialized")
    def test_wait_for_result_success(self, mock_ray_initialized, mock_ray_get):
        """Test wait_for_result succeeds."""
        mock_ray_initialized.return_value = True
        mock_ray_get.return_value = "result"

        # Create a mock ObjectRef
        mock_future = Mock(spec=ray.ObjectRef)

        result = RayExecutor.wait_for_result(mock_future)

        assert result == "result"
        mock_ray_get.assert_called_once_with(mock_future)

    @patch("ray.get")
    @patch("ray.is_initialized")
    def test_wait_for_result_ray_error(self, mock_ray_initialized, mock_ray_get):
        """Test wait_for_result raises RayError when ray.get fails."""
        mock_ray_initialized.return_value = True
        mock_ray_get.side_effect = Exception("Ray get failed")

        # Create a mock ObjectRef
        mock_future = Mock(spec=ray.ObjectRef)

        with pytest.raises(RayError, match="Error getting result from future"):
            RayExecutor.wait_for_result(mock_future)
