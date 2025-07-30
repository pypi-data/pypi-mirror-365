"""Tests for RayProcessManager class."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from ray_simplify.core import (
    SUBPROCESS_TIMEOUT_SECONDS,
    RayProcessError,
    RayProcessManager,
)


class TestRayProcessManager:
    """Test RayProcessManager class."""

    def test_ray_process_manager_init(self):
        """Test RayProcessManager initialization."""
        manager = RayProcessManager(num_cpus=4)
        assert manager._num_cpus == 4

    def test_ray_process_manager_init_invalid_cpus(self):
        """Test RayProcessManager raises ValueError for invalid num_cpus."""
        with pytest.raises(ValueError, match="num_cpus must be positive"):
            RayProcessManager(num_cpus=0)

        with pytest.raises(ValueError, match="num_cpus must be positive"):
            RayProcessManager(num_cpus=-1)

    @patch("subprocess.run")
    def test_get_ray_status_online(self, mock_subprocess_run):
        """Test get_ray_status returns online when Ray is running."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        manager = RayProcessManager()
        status = manager.get_ray_status()

        assert status == "online"
        mock_subprocess_run.assert_called_once_with(
            ["ray", "status"],
            capture_output=True,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
            text=True,
        )

    @patch("subprocess.run")
    def test_get_ray_status_offline(self, mock_subprocess_run):
        """Test get_ray_status returns offline when Ray is not running."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess_run.return_value = mock_result

        manager = RayProcessManager()
        status = manager.get_ray_status()

        assert status == "offline"

    @patch("subprocess.run")
    def test_get_ray_status_timeout(self, mock_subprocess_run):
        """Test get_ray_status handles timeout."""
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(
            ["ray", "status"], SUBPROCESS_TIMEOUT_SECONDS
        )

        manager = RayProcessManager()
        status = manager.get_ray_status()

        assert status == "offline"

    @patch("subprocess.run")
    def test_get_ray_status_file_not_found(self, mock_subprocess_run):
        """Test get_ray_status handles FileNotFoundError."""
        mock_subprocess_run.side_effect = FileNotFoundError("ray command not found")

        manager = RayProcessManager()
        status = manager.get_ray_status()

        assert status == "offline"

    @patch("subprocess.run")
    def test_get_ray_status_unexpected_error(self, mock_subprocess_run):
        """Test get_ray_status raises RayProcessError for unexpected errors."""
        mock_subprocess_run.side_effect = OSError("Unexpected error")

        manager = RayProcessManager()
        with pytest.raises(RayProcessError, match="Failed to check Ray status"):
            manager.get_ray_status()

    @patch("subprocess.run")
    def test_start_ray_success(self, mock_subprocess_run):
        """Test start_ray succeeds."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        manager = RayProcessManager(num_cpus=4)
        manager.start_ray()

        expected_command = [
            "ray",
            "start",
            "--head",
            "--num-cpus=4",
            "--disable-usage-stats",
        ]
        mock_subprocess_run.assert_called_once_with(
            expected_command,
            capture_output=True,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
            text=True,
        )

    @patch("subprocess.run")
    def test_start_ray_failure(self, mock_subprocess_run):
        """Test start_ray raises RayProcessError on failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Ray start failed"
        mock_subprocess_run.return_value = mock_result

        manager = RayProcessManager()
        with pytest.raises(
            RayProcessError, match="Ray start failed with return code 1"
        ):
            manager.start_ray()

    @patch("subprocess.run")
    def test_start_ray_timeout(self, mock_subprocess_run):
        """Test start_ray raises RayProcessError on timeout."""
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(
            ["ray", "start"], SUBPROCESS_TIMEOUT_SECONDS
        )

        manager = RayProcessManager()
        with pytest.raises(RayProcessError, match="Ray start timed out"):
            manager.start_ray()

    @patch("subprocess.run")
    def test_start_ray_file_not_found(self, mock_subprocess_run):
        """Test start_ray raises RayProcessError when Ray CLI not found."""
        mock_subprocess_run.side_effect = FileNotFoundError("ray command not found")

        manager = RayProcessManager()
        with pytest.raises(RayProcessError, match="Ray CLI not found in PATH"):
            manager.start_ray()

    @patch("subprocess.run")
    def test_start_ray_unexpected_error(self, mock_subprocess_run):
        """Test start_ray raises RayProcessError for unexpected errors."""
        mock_subprocess_run.side_effect = OSError("Unexpected error")

        manager = RayProcessManager()
        with pytest.raises(RayProcessError, match="Failed to start Ray"):
            manager.start_ray()

    @patch("subprocess.run")
    def test_stop_ray_success(self, mock_subprocess_run):
        """Test stop_ray succeeds."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        manager = RayProcessManager()
        manager.stop_ray()  # Should not raise

        mock_subprocess_run.assert_called_once_with(
            ["ray", "stop"],
            capture_output=True,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
            text=True,
        )

    @patch("subprocess.run")
    def test_stop_ray_failure(self, mock_subprocess_run):
        """Test stop_ray handles failure gracefully."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Ray stop failed"
        mock_subprocess_run.return_value = mock_result

        manager = RayProcessManager()
        manager.stop_ray()  # Should not raise, just log warning

    @patch("subprocess.run")
    def test_stop_ray_timeout(self, mock_subprocess_run):
        """Test stop_ray handles timeout gracefully."""
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired(
            ["ray", "stop"], SUBPROCESS_TIMEOUT_SECONDS
        )

        manager = RayProcessManager()
        manager.stop_ray()  # Should not raise, just log warning

    @patch("subprocess.run")
    def test_stop_ray_file_not_found(self, mock_subprocess_run):
        """Test stop_ray handles FileNotFoundError gracefully."""
        mock_subprocess_run.side_effect = FileNotFoundError("ray command not found")

        manager = RayProcessManager()
        manager.stop_ray()  # Should not raise, just log warning

    @patch("subprocess.run")
    def test_stop_ray_unexpected_error(self, mock_subprocess_run):
        """Test stop_ray handles unexpected errors gracefully."""
        mock_subprocess_run.side_effect = OSError("Unexpected error")

        manager = RayProcessManager()
        manager.stop_ray()  # Should not raise, just log error
