"""Tests for ParallelContext initialization validation."""

import pytest

from ray_simplify.core import ParallelContext


class TestParallelContextValidation:
    """Test ParallelContext initialization validation."""

    def test_parallel_context_invalid_num_cpus(self):
        """Test ParallelContext raises ValueError for invalid num_cpus."""
        with pytest.raises(ValueError, match="num_cpus must be positive"):
            ParallelContext(num_cpus=0)

        with pytest.raises(ValueError, match="num_cpus must be positive"):
            ParallelContext(num_cpus=-1)

    def test_parallel_context_invalid_on_host(self):
        """Test ParallelContext raises ValueError for invalid on_host."""
        with pytest.raises(ValueError, match="on_host must be a string"):
            ParallelContext(on_host=123)

        with pytest.raises(ValueError, match="on_host must be a string"):
            ParallelContext(on_host=[])

    def test_parallel_context_invalid_log_level(self):
        """Test ParallelContext raises ValueError for invalid log_level."""
        with pytest.raises(ValueError, match="log_level must be a valid logging level"):
            ParallelContext(log_level="INVALID")

        with pytest.raises(ValueError, match="log_level must be a valid logging level"):
            ParallelContext(log_level="debug")  # Must be uppercase

    def test_parallel_context_valid_initialization(self):
        """Test ParallelContext initializes with valid parameters."""
        ctx = ParallelContext(
            num_cpus=4, on_host="localhost", log_level="DEBUG", log_to_driver=False
        )
        assert ctx._num_cpus == 4
        assert ctx._on_host == "localhost"
        assert ctx._log_level == "DEBUG"
        assert ctx._log_to_driver is False
