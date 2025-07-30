"""Tests for ParallelContext static methods and missing coverage paths."""

from unittest.mock import MagicMock, patch

import pytest

from ray_simplify.core import ParallelContext, RayInitializationError
from ray_simplify.executor import RayExecutor


class TestParallelContextStaticMethods:
    """Test ParallelContext static methods to achieve 100% coverage."""

    @patch.object(RayExecutor, "shared")
    def test_shared_method_delegates_to_executor(self, mock_shared):
        """Test that _shared method delegates to RayExecutor.shared."""
        mock_shared.return_value = "shared_object_ref"
        test_data = [1, 2, 3, 4]

        result = ParallelContext._shared(test_data)

        assert result == "shared_object_ref"
        mock_shared.assert_called_once_with(test_data)

    @patch.object(RayExecutor, "map_parallel")
    def test_map_method_delegates_to_executor(self, mock_map_parallel):
        """Test that _map method delegates to RayExecutor.map_parallel."""
        expected_result = iter([1, 4, 9, 16])
        mock_map_parallel.return_value = expected_result

        def square(x):
            return x * x

        test_args = [1, 2, 3, 4]

        result = ParallelContext._map(square, test_args, timeout=30)

        assert result is expected_result
        mock_map_parallel.assert_called_once_with(square, test_args, timeout=30)

    @patch.object(RayExecutor, "iter_futures")
    def test_iter_method_delegates_to_executor(self, mock_iter_futures):
        """Test that _iter method delegates to RayExecutor.iter_futures."""
        expected_result = iter([1, 2, 3])
        mock_iter_futures.return_value = expected_result
        test_futures = ["future1", "future2", "future3"]

        result = ParallelContext._iter(test_futures)

        assert result is expected_result
        mock_iter_futures.assert_called_once_with(test_futures)

    @patch.object(RayExecutor, "wait_for_result")
    def test_wait_method_delegates_to_executor(self, mock_wait_for_result):
        """Test that _wait method delegates to RayExecutor.wait_for_result."""
        mock_wait_for_result.return_value = 42
        test_future = "test_future_ref"

        result = ParallelContext._wait(test_future)

        assert result == 42
        mock_wait_for_result.assert_called_once_with(test_future)


class TestParallelContextErrorHandling:
    """Test ParallelContext error handling paths for missing coverage."""

    @patch("ray.init")
    @patch("ray.is_initialized")
    def test_enter_initialization_failure_with_self_hosted_cleanup_error(
        self, mock_ray_initialized, mock_ray_init
    ):
        """Test __enter__ with initialization failure and cleanup error."""
        # Setup: Ray initialization fails and cleanup also fails
        mock_ray_init.side_effect = Exception("Ray init failed")
        mock_ray_initialized.return_value = False

        # Mock process manager to simulate self-hosted scenario and cleanup failure
        mock_process_manager = MagicMock()
        mock_process_manager.get_ray_status.return_value = "offline"  # self-hosted
        mock_process_manager.start_ray.return_value = None
        mock_process_manager.stop_ray.side_effect = Exception("Cleanup failed")

        ctx = ParallelContext()
        ctx._process_manager = mock_process_manager

        # Test: Should raise RayInitializationError and attempt cleanup
        with pytest.raises(
            RayInitializationError, match="Failed to initialize Ray context"
        ):
            with patch("ray_simplify.context.log") as mock_log:
                ctx.__enter__()

        # Verify cleanup was attempted and error was logged
        mock_process_manager.stop_ray.assert_called_once()
        # The log.error call should have been made for the cleanup error
        mock_log.error.assert_called_once()

    @patch("ray.init")
    @patch("ray.is_initialized")
    def test_enter_initialization_failure_with_successful_cleanup(
        self, mock_ray_initialized, mock_ray_init
    ):
        """Test __enter__ with initialization failure but successful cleanup."""
        # Setup: Ray initialization fails but cleanup succeeds
        mock_ray_init.side_effect = Exception("Ray init failed")
        mock_ray_initialized.return_value = False

        # Mock process manager to simulate self-hosted scenario with successful cleanup
        mock_process_manager = MagicMock()
        mock_process_manager.get_ray_status.return_value = "offline"  # self-hosted
        mock_process_manager.start_ray.return_value = None
        mock_process_manager.stop_ray.return_value = None  # successful cleanup

        ctx = ParallelContext()
        ctx._process_manager = mock_process_manager

        # Test: Should raise RayInitializationError but cleanup should succeed
        with pytest.raises(
            RayInitializationError, match="Failed to initialize Ray context"
        ):
            ctx.__enter__()

        # Verify cleanup was attempted
        mock_process_manager.stop_ray.assert_called_once()
