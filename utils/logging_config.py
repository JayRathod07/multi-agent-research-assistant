"""
Logging configuration for the Multi-Agent Research Assistant.

Call setup_logging() once at application startup to configure
both a console handler and a rotating file handler.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "pipeline.log",
) -> logging.Logger:
    """
    Configure application-wide logging.

    Args:
        log_level: Minimum level for console output (DEBUG, INFO, WARNING, ERROR).
        log_file:  Path to the log file (DEBUG and above always written here).

    Returns:
        The root logger, ready to use.
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- Console handler ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)

    # --- File handler (rotating, max 5 MB × 3 backups) ---
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # Always capture full detail to file
    file_handler.setFormatter(formatter)

    # --- Root logger ---
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if setup_logging() is called more than once
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Convenience wrapper — returns a named logger."""
    return logging.getLogger(name)
