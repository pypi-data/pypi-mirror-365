"""Tests for module constants."""

from ray_simplify.core import (
    DEFAULT_LOG_LEVEL,
    DEFAULT_NUM_CPUS,
    DEFAULT_RAY_PORT,
    SUBPROCESS_TIMEOUT_SECONDS,
)


class TestConstants:
    """Test module constants are properly defined."""

    def test_constants_exist(self):
        """Test that all expected constants exist and have correct types."""
        assert isinstance(DEFAULT_NUM_CPUS, int)
        assert DEFAULT_NUM_CPUS > 0

        assert isinstance(DEFAULT_RAY_PORT, int)
        assert DEFAULT_RAY_PORT > 0

        assert isinstance(SUBPROCESS_TIMEOUT_SECONDS, int)
        assert SUBPROCESS_TIMEOUT_SECONDS > 0

        assert isinstance(DEFAULT_LOG_LEVEL, str)
        assert DEFAULT_LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
