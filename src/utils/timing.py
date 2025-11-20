"""
Time measurement and performance tracking utilities.

Provides decorators and context managers for:
- Function execution timing
- Performance monitoring
- Bottleneck identification
- Statistical timing analysis
"""

import time
import functools
from typing import Callable, Any, Dict, Optional, List
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class TimingStats:
    """Container for timing statistics."""
    
    function_name: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    times: List[float] = field(default_factory=list)
    
    def add_measurement(self, duration: float) -> None:
        """Add a new timing measurement."""
        self.call_count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.times.append(duration)
    
    @property
    def avg_time(self) -> float:
        """Calculate average execution time."""
        return self.total_time / self.call_count if self.call_count > 0 else 0.0
    
    @property
    def median_time(self) -> float:
        """Calculate median execution time."""
        return statistics.median(self.times) if self.times else 0.0
    
    @property
    def std_dev(self) -> float:
        """Calculate standard deviation of execution times."""
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            "function": self.function_name,
            "calls": self.call_count,
            "total_time_sec": round(self.total_time, 4),
            "avg_time_sec": round(self.avg_time, 4),
            "median_time_sec": round(self.median_time, 4),
            "min_time_sec": round(self.min_time, 4),
            "max_time_sec": round(self.max_time, 4),
            "std_dev_sec": round(self.std_dev, 4),
        }


class TimingTracker:
    """Global timing tracker for all timed functions."""
    
    _instance: Optional['TimingTracker'] = None
    _stats: Dict[str, TimingStats] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._stats = defaultdict(lambda: TimingStats("unknown"))
        return cls._instance
    
    def record(self, function_name: str, duration: float) -> None:
        """Record timing for a function."""
        try:
            if function_name not in self._stats:
                self._stats[function_name] = TimingStats(function_name)
            self._stats[function_name].add_measurement(duration)
        except Exception as e:
            logger.error(f"Failed to record timing: {e}")
    
    def get_stats(self, function_name: Optional[str] = None) -> Dict[str, Any]:
        """Get timing statistics."""
        try:
            if function_name:
                return self._stats.get(function_name, TimingStats(function_name)).get_summary()
            return {name: stats.get_summary() for name, stats in self._stats.items()}
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    def reset(self, function_name: Optional[str] = None) -> None:
        """Reset timing statistics."""
        try:
            if function_name:
                if function_name in self._stats:
                    del self._stats[function_name]
            else:
                self._stats.clear()
        except Exception as e:
            logger.error(f"Failed to reset stats: {e}")


# Global tracker instance
_tracker = TimingTracker()


def measure_time(
    log_level: str = "info",
    log_result: bool = True,
    track_stats: bool = True,
) -> Callable:
    """
    Decorator to measure and log function execution time.
    
    Args:
        log_level: Log level for timing info (debug, info, warning)
        log_result: Whether to log the timing result
        track_stats: Whether to track statistics for this function
    
    Returns:
        Decorated function
    
    Example:
        @measure_time()
        def slow_function():
            time.sleep(1)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            function_name = f"{func.__module__}.{func.__name__}"
            start_time = time.perf_counter()
            exception_occurred = False
            result = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                exception_occurred = True
                logger.error(f"Exception in {function_name}: {e}")
                raise
            finally:
                # Always measure time, even on exception
                end_time = time.perf_counter()
                duration = end_time - start_time
                
                # Track statistics
                if track_stats:
                    try:
                        _tracker.record(function_name, duration)
                    except Exception as track_error:
                        logger.error(f"Failed to track timing: {track_error}")
                
                # Log result
                if log_result:
                    try:
                        status = "FAILED" if exception_occurred else "OK"
                        time_str = format_duration(duration)
                        log_message = f"{function_name} | {status} | {time_str}"
                        
                        log_method = getattr(logger, log_level.lower(), logger.info)
                        log_method(log_message)
                    except Exception as log_error:
                        logger.error(f"Failed to log timing: {log_error}")
        
        return wrapper
    return decorator


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "1.23s", "123ms", "1.23μs")
    """
    try:
        if seconds >= 1:
            return f"{seconds:.2f}s"
        elif seconds >= 0.001:
            return f"{seconds * 1000:.2f}ms"
        elif seconds >= 0.000001:
            return f"{seconds * 1000000:.2f}μs"
        else:
            return f"{seconds * 1000000000:.2f}ns"
    except Exception:
        return f"{seconds}s"


class Timer:
    """Context manager for timing code blocks."""
    
    def __init__(
        self,
        name: str = "operation",
        log_level: str = "info",
        auto_log: bool = True,
    ):
        """
        Initialize timer.
        
        Args:
            name: Name of the operation being timed
            log_level: Log level for results
            auto_log: Automatically log when exiting context
        """
        self.name = name
        self.log_level = log_level
        self.auto_log = auto_log
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
    
    def __enter__(self) -> 'Timer':
        """Start timing."""
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Stop timing and optionally log."""
        self.end_time = time.perf_counter()
        if self.start_time is not None:
            self.duration = self.end_time - self.start_time
            
            if self.auto_log:
                try:
                    status = "FAILED" if exc_type else "OK"
                    time_str = format_duration(self.duration)
                    log_message = f"{self.name} | {status} | {time_str}"
                    
                    log_method = getattr(logger, self.log_level.lower(), logger.info)
                    log_method(log_message)
                except Exception as e:
                    logger.error(f"Failed to log timer: {e}")
    
    def elapsed(self) -> float:
        """Get elapsed time (can be called during execution)."""
        if self.start_time is None:
            return 0.0
        current_time = time.perf_counter()
        return current_time - self.start_time


def get_timing_stats(function_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get timing statistics for tracked functions.
    
    Args:
        function_name: Specific function name, or None for all
    
    Returns:
        Dictionary of timing statistics
    """
    return _tracker.get_stats(function_name)


def reset_timing_stats(function_name: Optional[str] = None) -> None:
    """
    Reset timing statistics.
    
    Args:
        function_name: Specific function name, or None for all
    """
    _tracker.reset(function_name)


def print_timing_report() -> None:
    """Print a formatted report of all timing statistics."""
    try:
        stats = get_timing_stats()
        if not stats:
            logger.info("No timing data available")
            return
        
        logger.info("=" * 80)
        logger.info("TIMING REPORT")
        logger.info("=" * 80)
        
        # Sort by total time descending
        sorted_stats = sorted(
            stats.items(),
            key=lambda x: x[1].get("total_time_sec", 0),
            reverse=True
        )
        
        for func_name, func_stats in sorted_stats:
            logger.info(f"\n{func_name}:")
            for key, value in func_stats.items():
                if key != "function":
                    logger.info(f"  {key}: {value}")
        
        logger.info("=" * 80)
    except Exception as e:
        logger.error(f"Failed to print timing report: {e}")
