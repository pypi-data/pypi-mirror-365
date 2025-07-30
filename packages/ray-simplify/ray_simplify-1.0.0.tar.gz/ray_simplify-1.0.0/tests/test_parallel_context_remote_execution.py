"""Tests for ParallelContext remote execution scenarios."""

from unittest.mock import patch

import pytest

from ray_simplify.core import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_RAY_PORT,
    ParallelContext,
    RayInitializationError,
    RayProcessManager,
)


class TestParallelContextRemoteExecution:
    """Test ParallelContext remote execution scenarios."""

    @patch("ray.init")
    def test_enter_remote_host_success(self, mock_ray_init):
        """Test __enter__ with remote host succeeds."""
        ctx = ParallelContext(on_host="192.168.1.100", num_cpus=4)

        result = ctx.__enter__()

        assert result is ctx
        mock_ray_init.assert_called_once_with(
            address=f"ray://192.168.1.100:{DEFAULT_RAY_PORT}",
            log_to_driver=True,
            runtime_env={"working_dir": ".", "excludes": [".git/*"]},
            logging_level=DEFAULT_LOG_LEVEL,
        )

    @patch("ray.init")
    def test_enter_remote_host_failure(self, mock_ray_init):
        """Test __enter__ with remote host handles failure."""
        mock_ray_init.side_effect = Exception("Connection failed")
        ctx = ParallelContext(on_host="192.168.1.100")

        with pytest.raises(
            RayInitializationError, match="Failed to initialize Ray context"
        ):
            ctx.__enter__()

    @patch("ray.is_initialized")
    @patch("ray.init")
    def test_enter_local_ray_already_initialized(
        self, mock_ray_init, mock_ray_initialized
    ):
        """Test __enter__ when Ray is already initialized locally."""
        mock_ray_initialized.return_value = True

        with patch.object(RayProcessManager, "get_ray_status", return_value="online"):
            ctx = ParallelContext()
            result = ctx.__enter__()

            assert result is ctx
            assert not ctx._is_self_hosted
            mock_ray_init.assert_not_called()

    @patch("ray.is_initialized")
    @patch("ray.init")
    def test_enter_local_ray_not_initialized(self, mock_ray_init, mock_ray_initialized):
        """Test __enter__ when Ray is not initialized locally."""
        mock_ray_initialized.return_value = False

        with patch.object(RayProcessManager, "get_ray_status", return_value="online"):
            ctx = ParallelContext()
            result = ctx.__enter__()

            assert result is ctx
            assert not ctx._is_self_hosted
            mock_ray_init.assert_called_once()

    @patch("ray.is_initialized")
    @patch("ray.init")
    def test_enter_local_start_new_cluster(self, mock_ray_init, mock_ray_initialized):
        """Test __enter__ starts new Ray cluster when needed."""
        mock_ray_initialized.return_value = False

        with patch.object(RayProcessManager, "get_ray_status", return_value="offline"):
            with patch.object(RayProcessManager, "start_ray") as mock_start:
                ctx = ParallelContext()
                result = ctx.__enter__()

                assert result is ctx
                assert ctx._is_self_hosted
                mock_start.assert_called_once()
                mock_ray_init.assert_called_once()

    @patch("ray.is_initialized")
    @patch("ray.init")
    def test_enter_initialization_failure_with_cleanup(
        self, mock_ray_init, mock_ray_initialized
    ):
        """Test __enter__ cleans up on initialization failure."""
        mock_ray_initialized.return_value = False
        mock_ray_init.side_effect = Exception("Init failed")

        with patch.object(RayProcessManager, "get_ray_status", return_value="offline"):
            with patch.object(RayProcessManager, "start_ray"):
                with patch.object(RayProcessManager, "stop_ray") as mock_stop:
                    ctx = ParallelContext()

                    with pytest.raises(RayInitializationError):
                        ctx.__enter__()

                    mock_stop.assert_called_once()

    @patch("ray.is_initialized")
    @patch("ray.shutdown")
    def test_exit_ray_initialized(self, mock_ray_shutdown, mock_ray_initialized):
        """Test __exit__ when Ray is initialized."""
        mock_ray_initialized.return_value = True

        ctx = ParallelContext()
        ctx._is_self_hosted = False
        ctx.__exit__(None, None, None)

        mock_ray_shutdown.assert_called_once_with(_exiting_interpreter=True)

    @patch("ray.is_initialized")
    @patch("ray.shutdown")
    def test_exit_self_hosted_cluster(self, mock_ray_shutdown, mock_ray_initialized):
        """Test __exit__ stops self-hosted cluster."""
        mock_ray_initialized.return_value = True

        with patch.object(RayProcessManager, "stop_ray") as mock_stop:
            ctx = ParallelContext()
            ctx._is_self_hosted = True
            ctx.__exit__(None, None, None)

            mock_ray_shutdown.assert_called_once()
            mock_stop.assert_called_once()

    @patch("ray.is_initialized")
    @patch("ray.shutdown")
    def test_exit_with_exception(self, mock_ray_shutdown, mock_ray_initialized):
        """Test __exit__ handles exceptions gracefully."""
        mock_ray_initialized.return_value = True
        mock_ray_shutdown.side_effect = Exception("Shutdown failed")

        ctx = ParallelContext()
        ctx._is_self_hosted = False

        # Should not raise exception
        ctx.__exit__(None, None, None)
