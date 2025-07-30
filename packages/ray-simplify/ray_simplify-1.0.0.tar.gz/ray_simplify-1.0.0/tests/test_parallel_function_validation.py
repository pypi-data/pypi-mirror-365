"""Tests for parallel function parameter validation."""

import pytest

from ray_simplify.core import parallel


class TestParallelFunctionValidation:
    """Test parallel function parameter validation."""

    def test_parallel_invalid_parameters(self):
        """Test parallel function with invalid parameters."""
        with pytest.raises(ValueError):
            parallel(num_cpus=0)

        with pytest.raises(ValueError):
            parallel(on_host=123)

        with pytest.raises(ValueError):
            parallel(log_level="invalid")
