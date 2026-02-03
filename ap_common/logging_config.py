"""
Logging configuration for ap-common.

This module provides a centralized logging setup that can be used
consistently across all ap-common tools and dependent projects.

Example usage in another module:
    from ap_common.logging_config import setup_logging
    logger = setup_logging(name="my_tool", debug=True)
    logger.info("Starting my_tool")

Generated to address GitHub Issues #8 and #11.
"""

import logging
import sys

# Default log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Module-level logger
_logger = None


def setup_logging(
    name: str = "ap_common",
    debug: bool = False,
    quiet: bool = False,
    log_format: str = LOG_FORMAT,
    date_format: str = DATE_FORMAT,
):
    """
    Sets up and returns a configured logger for ap-common and related tools.

    This function provides a consistent logging configuration that can be
    bootstrapped from ap-common in all dependent projects.

    Args:
        name: Logger name (defaults to "ap_common")
        debug: If True, sets log level to DEBUG (overrides quiet)
        quiet: If True, sets log level to WARNING (suppresses INFO)
        log_format: Custom log format string (defaults to LOG_FORMAT)
        date_format: Custom date format string (defaults to DATE_FORMAT)

    Returns:
        Configured logger instance

    Logging Level Behavior:
        | debug | quiet | Level   | Messages Shown           |
        |-------|-------|---------|--------------------------|
        | False | False | INFO    | INFO, WARNING, ERROR     |
        | False | True  | WARNING | WARNING, ERROR           |
        | True  | False | DEBUG   | DEBUG, INFO, WARNING, ERROR |
        | True  | True  | DEBUG   | DEBUG, INFO, WARNING, ERROR |

    Note: The debug flag overrides quiet mode. When debug=True, all messages
    are shown regardless of the quiet setting.
    """
    logger = logging.getLogger(name)

    # Clear existing handlers to prevent duplicates
    logger.handlers.clear()

    # Set log level based on flags
    if debug:
        level = logging.DEBUG  # Debug overrides quiet
    elif quiet:
        level = logging.WARNING  # Quiet suppresses INFO
    else:
        level = logging.INFO  # Default
    logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = None):
    """
    Gets or creates a logger with the given name.

    If no name is provided, returns the default ap_common logger.
    If the default logger hasn't been set up, creates one with default settings.

    Args:
        name: Optional logger name. If None, uses "ap_common"

    Returns:
        Logger instance
    """
    global _logger
    logger_name = name or "ap_common"

    if name is None:
        # Return the default logger, creating it if needed
        if _logger is None:
            _logger = setup_logging()
        return _logger

    # Return a child logger for specific modules
    return logging.getLogger(logger_name)
