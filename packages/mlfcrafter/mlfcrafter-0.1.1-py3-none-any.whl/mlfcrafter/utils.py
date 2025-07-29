"""
MLFCrafter Logging Utilities
============================

Centralized logging configuration for MLFCrafter pipeline operations.
"""

import logging
import sys


def setup_logger(name: str = "mlfcrafter", level: str = "INFO") -> logging.Logger:
    """
    Setup MLFCrafter logger with consistent formatting.

    Args:
        name: Logger name (default: "mlfcrafter")
        level: Log level ("DEBUG", "INFO", "WARNING", "ERROR")

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_crafter_logger(crafter_name: str) -> logging.Logger:
    """
    Get logger for specific crafter.

    Args:
        crafter_name: Name of the crafter class

    Returns:
        Logger instance for the crafter
    """
    return logging.getLogger(f"mlfcrafter.{crafter_name}")


# Initialize default logger
default_logger = setup_logger()
