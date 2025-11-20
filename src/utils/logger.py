"""
Enterprise-grade logging system with colored console output, file rotation, and error handling.

Features:
- Colored console output (using Rich library)
- File rotation (10MB, 5 backups)
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Context logging with structured data
- Multiple fallback layers for error handling
- Performance metrics tracking
- Thread-safe operation

Example:
    >>> from src.utils.logger import get_logger, setup_logger
    >>> setup_logger(name="my_app", log_file="app.log", level="INFO")
    >>> logger = get_logger("my_app.module")
    >>> logger.info("Application started", extra={"user": "admin", "pid": 12345})
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

# Try to import Rich for colored console output, fallback to standard logging
try:
    from rich.console import Console
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not available. Install with: pip install rich", file=sys.stderr)


# Global logger registry
_LOGGERS: Dict[str, logging.Logger] = {}
_DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_RICH_FORMAT = "%(message)s"


class StructuredFormatter(logging.Formatter):
    """Custom formatter that handles structured logging with extra fields."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured data if present."""
        # Store original format
        original_format = self._style._fmt

        # Add structured data if present
        if hasattr(record, 'structured_data'):
            try:
                structured = json.dumps(record.structured_data, indent=2)
                record.msg = f"{record.msg}\nStructured Data: {structured}"
            except (TypeError, ValueError) as e:
                record.msg = f"{record.msg}\n[Error serializing structured data: {e}]"

        # Format the record
        result = super().format(record)

        # Restore original format
        self._style._fmt = original_format

        return result


def setup_logger(
    name: str = "longevity-rag",
    log_file: Optional[str] = None,
    level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    use_rich: bool = True,
    log_dir: Optional[Path] = None
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.

    Args:
        name: Logger name (hierarchical, e.g., "app.module")
        log_file: Log file name (optional). If None, only console logging is enabled.
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep
        use_rich: Use Rich library for colored console output (if available)
        log_dir: Directory for log files (default: logs/ in project root)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logger("my_app", log_file="app.log", level="DEBUG")
        >>> logger.info("Application started")
    """
    # Check if logger already exists
    if name in _LOGGERS:
        return _LOGGERS[name]

    # Create logger
    logger = logging.getLogger(name)

    # Validate and set log level with fallback
    try:
        log_level = getattr(logging, level.upper())
        logger.setLevel(log_level)
    except AttributeError:
        print(f"Warning: Invalid log level '{level}', falling back to INFO", file=sys.stderr)
        logger.setLevel(logging.INFO)

    logger.propagate = False  # Don't propagate to root logger

    # Remove existing handlers (prevents duplicates)
    logger.handlers.clear()

    try:
        # Console handler
        if RICH_AVAILABLE and use_rich:
            # Rich console handler (colored output)
            console = Console(stderr=True)
            console_handler = RichHandler(
                console=console,
                rich_tracebacks=True,
                tracebacks_show_locals=True,
                show_time=True,
                show_level=True,
                show_path=True,
                markup=True,
                log_time_format="[%Y-%m-%d %H:%M:%S]"
            )
            console_handler.setFormatter(logging.Formatter(_RICH_FORMAT))
        else:
            # Standard console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = StructuredFormatter(
                _DEFAULT_FORMAT,
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_formatter)

        logger.addHandler(console_handler)

        # File handler (if log_file is specified)
        if log_file:
            # Determine log directory
            if log_dir is None:
                # Default: logs/ directory in project root
                project_root = Path(__file__).parent.parent.parent
                log_dir = project_root / "logs"

            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)

            log_path = log_dir / log_file

            # Rotating file handler
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_formatter = StructuredFormatter(
                _DEFAULT_FORMAT,
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            logger.info(f"Logging to file: {log_path}")

    except Exception as e:
        # Fallback: basic console logging
        print(f"Error setting up logger: {e}", file=sys.stderr)
        fallback_handler = logging.StreamHandler(sys.stderr)
        fallback_handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        logger.addHandler(fallback_handler)
        logger.error(f"Failed to set up full logging, using fallback: {e}")

    # Register logger
    _LOGGERS[name] = logger

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the specified name.

    If the logger doesn't exist, creates it with default settings.
    For hierarchical logging, use dot notation (e.g., "app.module.submodule").

    Args:
        name: Logger name (hierarchical)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger("my_app.database")
        >>> logger.warning("Connection pool exhausted")
    """
    if name in _LOGGERS:
        return _LOGGERS[name]

    # Create logger with default settings
    return setup_logger(name=name, log_file=None, level="INFO")


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context: Any
) -> None:
    """
    Log a message with structured context data.

    Args:
        logger: Logger instance
        level: Log level (info, warning, error, etc.)
        message: Log message
        **context: Additional context as keyword arguments

    Example:
        >>> logger = get_logger("my_app")
        >>> log_with_context(
        ...     logger,
        ...     "info",
        ...     "User logged in",
        ...     user_id=123,
        ...     ip_address="192.168.1.1",
        ...     timestamp=datetime.now()
        ... )
    """
    try:
        # Get log method
        log_method = getattr(logger, level.lower())

        # Create LogRecord with structured data
        extra_dict = {"structured_data": context}

        log_method(message, extra=extra_dict)

    except Exception as e:
        logger.error(f"Error in log_with_context: {e}")


def log_exception(
    logger: logging.Logger,
    message: str = "An error occurred",
    exc_info: bool = True,
    **context: Any
) -> None:
    """
    Log an exception with traceback and context.

    Args:
        logger: Logger instance
        message: Error message
        exc_info: Include exception info (traceback)
        **context: Additional context as keyword arguments

    Example:
        >>> logger = get_logger("my_app")
        >>> try:
        ...     risky_operation()
        ... except Exception:
        ...     log_exception(logger, "Operation failed", operation="risky", user=user_id)
    """
    try:
        if context:
            extra_dict = {"structured_data": context}
            logger.error(message, exc_info=exc_info, extra=extra_dict)
        else:
            logger.error(message, exc_info=exc_info)

    except Exception as e:
        # Last resort fallback
        print(f"CRITICAL: Failed to log exception: {e}", file=sys.stderr)
        print(f"Original message: {message}", file=sys.stderr)


# Performance tracking
class LoggingTimer:
    """Context manager for timing operations with automatic logging."""

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        level: str = "info",
        **context: Any
    ):
        """
        Initialize timer.

        Args:
            logger: Logger instance
            operation: Operation name
            level: Log level for timing message
            **context: Additional context
        """
        self.logger = logger
        self.operation = operation
        self.level = level
        self.context = context
        self.start_time: Optional[datetime] = None

    def __enter__(self):
        """Start timer."""
        self.start_time = datetime.now()
        log_with_context(
            self.logger,
            self.level,
            f"Starting: {self.operation}",
            **self.context
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and log duration."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()

            if exc_type:
                log_with_context(
                    self.logger,
                    "error",
                    f"Failed: {self.operation} (duration: {duration:.3f}s)",
                    duration_seconds=duration,
                    error_type=exc_type.__name__,
                    **self.context
                )
            else:
                log_with_context(
                    self.logger,
                    self.level,
                    f"Completed: {self.operation} (duration: {duration:.3f}s)",
                    duration_seconds=duration,
                    **self.context
                )


# Module-level convenience logger
_default_logger = None


def get_default_logger() -> logging.Logger:
    """Get the default application logger."""
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_logger(
            name="longevity-rag",
            log_file="app.log",
            level="INFO"
        )
    return _default_logger


# Convenience functions using default logger
def info(message: str, **context: Any) -> None:
    """Log info message with default logger."""
    log_with_context(get_default_logger(), "info", message, **context)


def warning(message: str, **context: Any) -> None:
    """Log warning message with default logger."""
    log_with_context(get_default_logger(), "warning", message, **context)


def error(message: str, **context: Any) -> None:
    """Log error message with default logger."""
    log_with_context(get_default_logger(), "error", message, **context)


def debug(message: str, **context: Any) -> None:
    """Log debug message with default logger."""
    log_with_context(get_default_logger(), "debug", message, **context)


def critical(message: str, **context: Any) -> None:
    """Log critical message with default logger."""
    log_with_context(get_default_logger(), "critical", message, **context)


if __name__ == "__main__":
    # Demo
    demo_logger = setup_logger("demo", log_file="demo.log", level="DEBUG")

    demo_logger.debug("This is a debug message")
    demo_logger.info("Application started successfully")
    demo_logger.warning("This is a warning")

    log_with_context(
        demo_logger,
        "info",
        "User action",
        user_id=12345,
        action="login",
        ip="192.168.1.1"
    )

    with LoggingTimer(demo_logger, "database_query", query="SELECT * FROM users"):
        import time
        time.sleep(0.5)

    try:
        1 / 0
    except Exception:
        log_exception(demo_logger, "Math error occurred", operation="division")

    print("\nLogging demo complete! Check logs/demo.log for file output.")
