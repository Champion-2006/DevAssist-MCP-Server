"""
Centralized logging configuration for DevAssist MCP Server.

Provides structured logging with both console and rotating file output.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


_logging_configured = False


def setup_logging(
    level: str = "INFO",
    log_file: str = "logs/devassist.log",
) -> None:
    """
    Configure the root logger with console and file handlers.

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to the log file.
    """
    global _logging_configured
    if _logging_configured:
        return

    # Ensure log_file is an absolute path relative to project root
    if not os.path.isabs(log_file):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_file = os.path.join(project_root, log_file)

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Log format
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler (MUST log to sys.stderr so MCP stdio transport is never corrupted)
    import sys
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Rotating file handler (10 MB per file, keep 5 backups)
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # Fallback to system temp directory if project directory is read-only
        try:
            import tempfile

            temp_log = os.path.join(tempfile.gettempdir(), "devassist.log")
            file_handler = RotatingFileHandler(
                temp_log,
                maxBytes=10 * 1024 * 1024,
                backupCount=2,
                encoding="utf-8",
            )
            file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception:
            pass  # Fail silently to console/stderr

    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger instance.

    Ensures logging is configured before returning the logger.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured Logger instance.
    """
    if not _logging_configured:
        try:
            from config import settings

            setup_logging(
                level=settings.log_level,
                log_file=settings.log_file,
            )
        except ImportError:
            setup_logging()

    return logging.getLogger(name)
