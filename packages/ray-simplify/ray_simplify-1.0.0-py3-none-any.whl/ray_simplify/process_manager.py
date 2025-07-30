"""Ray process management functionality.

This module provides the RayProcessManager class for managing Ray cluster
processes via subprocess calls, including starting, stopping, and checking
the status of Ray clusters.
"""

import logging
import subprocess

from .constants import DEFAULT_NUM_CPUS, SUBPROCESS_TIMEOUT_SECONDS
from .exceptions import RayProcessError

log = logging.getLogger(__name__)


class RayProcessManager:
    """Manages Ray processes via subprocess calls.

    This class provides methods to start, stop, and check the status of Ray
    clusters using subprocess calls to the Ray CLI. It handles timeout,
    error conditions, and provides appropriate logging.

    Attributes:
        _num_cpus: Number of CPUs to allocate to the Ray cluster.

    Examples:
        >>> manager = RayProcessManager(num_cpus=4)
        >>> if manager.get_ray_status() == "offline":
        ...     manager.start_ray()
        >>> # Do work with Ray
        >>> manager.stop_ray()
    """

    def __init__(self, num_cpus: int = DEFAULT_NUM_CPUS):
        """Initialize the Ray process manager.

        Args:
            num_cpus: Number of CPUs to allocate to Ray. Must be positive.

        Raises:
            ValueError: If num_cpus is not positive.

        Examples:
            >>> manager = RayProcessManager()  # Uses default CPUs
            >>> manager = RayProcessManager(num_cpus=16)  # Custom CPU count
        """
        if num_cpus <= 0:
            raise ValueError("num_cpus must be positive")
        self._num_cpus = num_cpus

    def get_ray_status(self) -> str:
        """Check if Ray is running using subprocess.

        Returns:
            "online" if Ray is running, "offline" otherwise.

        Raises:
            RayProcessError: If the status check fails with unexpected error.

        Examples:
            >>> manager = RayProcessManager()
            >>> status = manager.get_ray_status()
            >>> if status == "online":
            ...     print("Ray is running")
        """
        try:
            result = subprocess.run(
                ["ray", "status"],
                capture_output=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
                text=True,
            )
            return "online" if result.returncode == 0 else "offline"
        except subprocess.TimeoutExpired:
            log.warning("Ray status check timed out")
            return "offline"
        except FileNotFoundError:
            log.warning("Ray CLI not found in PATH")
            return "offline"
        except Exception as e:
            raise RayProcessError(f"Failed to check Ray status: {e}") from e

    def start_ray(self) -> None:
        """Start Ray cluster via subprocess.

        Raises:
            RayProcessError: If Ray fails to start.

        Examples:
            >>> manager = RayProcessManager(num_cpus=8)
            >>> manager.start_ray()  # Starts Ray with 8 CPUs
        """
        command = [
            "ray",
            "start",
            "--head",
            f"--num-cpus={self._num_cpus}",
            "--disable-usage-stats",
        ]

        try:
            log.info(f"Starting Ray cluster with {self._num_cpus} CPUs")
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
                text=True,
            )

            if result.returncode != 0:
                raise RayProcessError(
                    f"Ray start failed with return code {result.returncode}. "
                    f"Error: {result.stderr}"
                )
            log.info("Ray cluster started successfully")

        except subprocess.TimeoutExpired:
            raise RayProcessError(
                f"Ray start timed out after {SUBPROCESS_TIMEOUT_SECONDS} seconds"
            ) from None
        except FileNotFoundError:
            raise RayProcessError("Ray CLI not found in PATH") from None
        except Exception as e:
            raise RayProcessError(f"Failed to start Ray: {e}") from e

    def stop_ray(self) -> None:
        """Stop Ray cluster via subprocess.

        This method gracefully handles errors and does not raise exceptions,
        as stopping Ray is often called during cleanup operations.

        Examples:
            >>> manager = RayProcessManager()
            >>> manager.stop_ray()  # Safely stops Ray cluster
        """
        try:
            log.info("Stopping Ray cluster")
            result = subprocess.run(
                ["ray", "stop"],
                capture_output=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
                text=True,
            )

            if result.returncode != 0:
                log.warning(
                    f"Ray stop returned code {result.returncode}: {result.stderr}"
                )
            else:
                log.info("Ray cluster stopped successfully")

        except subprocess.TimeoutExpired:
            log.warning(
                f"Ray stop timed out after {SUBPROCESS_TIMEOUT_SECONDS} seconds"
            )
        except FileNotFoundError:
            log.warning("Ray CLI not found in PATH")
        except Exception as e:
            log.error(f"Error stopping Ray: {e}")
