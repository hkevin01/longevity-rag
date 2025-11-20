"""
Unit tests for utility modules.

Tests logging, timing, and error handling functionality.
"""

import pytest
import time
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.logger import setup_logger, get_logger
from utils.timing import measure_time, Timer, format_duration, get_timing_stats


class TestLogger:
    """Test suite for logger functionality."""

    def test_setup_logger(self):
        """Test logger initialization."""
        logger = setup_logger(name="test_logger", level="DEBUG")
        assert logger is not None
        assert logger.name == "test_logger"

    def test_get_logger(self):
        """Test getting logger instance."""
        logger = get_logger("test")
        assert logger is not None

    def test_log_levels(self):
        """Test different log levels."""
        logger = setup_logger(name="test_levels", level="INFO")

        # Should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")


class TestTiming:
    """Test suite for timing functionality."""

    def test_format_duration(self):
        """Test duration formatting."""
        assert "s" in format_duration(1.5)
        assert "ms" in format_duration(0.001)
        assert "μs" in format_duration(0.000001)

    def test_timer_context_manager(self):
        """Test Timer context manager."""
        with Timer("test_operation", auto_log=False) as timer:
            time.sleep(0.01)

        assert timer.duration is not None
        assert timer.duration >= 0.01

    def test_measure_time_decorator(self):
        """Test measure_time decorator."""

        @measure_time(log_result=False)
        def slow_function():
            time.sleep(0.01)
            return "done"

        result = slow_function()
        assert result == "done"

        # Check stats were recorded
        stats = get_timing_stats()
        assert len(stats) > 0

    def test_timer_elapsed(self):
        """Test timer elapsed time tracking."""
        with Timer("test", auto_log=False) as timer:
            time.sleep(0.02)
            elapsed = timer.elapsed()
            assert elapsed >= 0.02


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def test_logger_with_invalid_level(self):
        """Test logger with invalid log level."""
        # Logger implementation handles invalid levels gracefully with fallback
        logger = setup_logger(name="test_invalid", level="INVALID")
        # Should still create a logger with fallback handler
        assert logger is not None
        assert logger.name == "test_invalid"

    def test_timer_without_context(self):
        """Test timer behavior without proper context."""
        timer = Timer("test", auto_log=False)
        # Should return 0 if not started
        assert timer.elapsed() == 0.0

    def test_empty_timing_stats(self):
        """Test getting stats when none recorded."""
        from utils.timing import reset_timing_stats
        reset_timing_stats()
        stats = get_timing_stats("nonexistent_function")
        assert "calls" in stats
        assert stats["calls"] == 0


def test_integration_logging_and_timing():
    """Integration test combining logging and timing."""
    logger = setup_logger(name="integration_test", level="INFO")

    @measure_time(log_result=False)
    def test_function():
        logger.info("Test function executing")
        time.sleep(0.01)
        return "success"

    result = test_function()
    assert result == "success"

    # Verify stats recorded
    stats = get_timing_stats()
    assert len(stats) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
