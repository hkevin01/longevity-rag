"""
Comprehensive logging utility for the Longevity RAG system.

Provides structured logging with:
- File rotation
- Console and file outputs
- Different log levels
- Context information
- Error tracking
- Performance metrics
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
from datetime import datetime

# ANSI color codes for console output
class LogColors:
    """ANSI color codes for console logging."""
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    LEVEL_COLORS = {
        logging.DEBUG: LogColors.CYAN,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.YELLOW,
        logging.ERROR: LogColors.RED,
        logging.CRITICAL: f"{LogColors.BOLD}{LogColors.RED}",
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors.

        Args:
            record: Log record to format

        Returns:
            Formatted and colored log string
        """
        try:
            # Get the base format
            log_message = super().format(record)

            # Add color if terminal supports it
            if sys.stderr.isatty():
                level_color = self.LEVEL_COLORS.get(record.levelno, LogColors.WHITE)
                return f"{level_color}{log_message}{LogColors.RESET}"

            return log_message
        except Exception as e:
            # Fallback if formatting fails
            return f"[LOGGING ERROR] {str(e)} | Original: {record.getMessage()}"


def setup_logger(
    name: str = "longevity_rag",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True,
    file_output: bool = True,
) -> logging.Logger:
    """
    Set up comprehensive logging with rotation and error handling.

    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name (default: {name}_{date}.log)
        log_dir: Directory for log files
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        console_output: Enable console output
        file_output: Enable file output

    Returns:
        Configured logger instance

    Raises:
        OSError: If log directory cannot be created
        ValueError: If invalid log level provided
    """
    try:
        # Validate log level
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_level}")

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(numeric_level)

        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()

        # Detailed format with timestamp, level, module, function, and message
        detailed_format = (
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(module)s:%(funcName)s:%(lineno)d | %(message)s"
        )
        date_format = "%Y-%m-%d %H:%M:%S"

        # Console handler with colors
        if console_output:
            try:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(numeric_level)
                console_formatter = ColoredFormatter(detailed_format, datefmt=date_format)
                console_handler.setFormatter(console_formatter)
                logger.addHandler(console_handler)
            except Exception as e:
                print(f"[ERROR] Failed to setup console logging: {e}", file=sys.stderr)

        # File handler with rotation
        if file_output:
            try:
                # Create log directory with proper permissions
                log_path = Path(log_dir)
                log_path.mkdir(parents=True, exist_ok=True)

                # Generate log file name if not provided
                if log_file is None:
                    timestamp = datetime.now().strftime("%Y%m%d")
                    log_file = f"{name}_{timestamp}.log"

                log_file_path = log_path / log_file

                # Rotating file handler for size-based rotation
                file_handler = RotatingFileHandler(
                    log_file_path,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding="utf-8",
                )
                file_handler.setLevel(numeric_level)
                file_formatter = logging.Formatter(detailed_format, datefmt=date_format)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

                # Log successful setup
                logger.info(f"Logging initialized: {log_file_path}")

            except PermissionError as e:
                print(f"[ERROR] Permission denied creating log file: {e}", file=sys.stderr)
                # Continue with console-only logging
            except OSError as e:
                print(f"[ERROR] Failed to create log directory: {e}", file=sys.stderr)
                raise

        # Prevent propagation to root logger
        logger.propagate = False

        return logger

    except Exception as e:
        # Fallback: create basic logger if setup fails
        print(f"[CRITICAL] Logger setup failed: {e}", file=sys.stderr)
        fallback_logger = logging.getLogger(name)
        fallback_logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        fallback_logger.addHandler(handler)
        return fallback_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (default: calling module name)

    Returns:
        Logger instance
    """
    try:
        if name is None:
            # Get the calling module's name
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back:
                caller_module = inspect.getmodule(frame.f_back)
                if caller_module:
                    name = caller_module.__name__
                else:
                    name = "longevity_rag"
            else:
                name = "longevity_rag"

        logger = logging.getLogger(name)

        # If logger has no handlers, set it up
        if not logger.handlers:
            log_level = os.getenv("LOG_LEVEL", "INFO")
            logger = setup_logger(name=name, log_level=log_level)

        return logger
    except Exception as e:
        # Absolute fallback
        print(f"[CRITICAL] Failed to get logger: {e}", file=sys.stderr)
        return logging.getLogger("fallback")


# Convenience function for logging with context
def log_with_context(logger: logging.Logger, level: str, message: str, **context):
    """
    Log message with additional context information.

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **context: Additional context key-value pairs
    """
    try:
        # Format context
        context_str = " | ".join(f"{k}={v}" for k, v in context.items()) if context else ""
        full_message = f"{message} | {context_str}" if context_str else message

        # Get logging method
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(full_message)
    except Exception as e:
        # Fallback logging if context logging fails
        logger.error(f"Failed to log with context: {e} | Original message: {message}")
