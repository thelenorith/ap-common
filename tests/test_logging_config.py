"""
Unit tests for ap_common.logging_config module.
"""

import logging
import pytest
from io import StringIO

from ap_common.logging_config import (
    setup_logging,
    get_logger,
    LOG_FORMAT,
    DATE_FORMAT,
)


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        logger = setup_logging(name="test_logger_1")
        assert isinstance(logger, logging.Logger)

    def test_default_name(self):
        """Test default logger name is 'ap_common'."""
        logger = setup_logging()
        assert logger.name == "ap_common"

    def test_custom_name(self):
        """Test custom logger name is used."""
        logger = setup_logging(name="custom_name")
        assert logger.name == "custom_name"

    def test_debug_level_false(self):
        """Test default log level is INFO when debug=False."""
        logger = setup_logging(name="test_logger_2", debug=False)
        assert logger.level == logging.INFO

    def test_debug_level_true(self):
        """Test log level is DEBUG when debug=True."""
        logger = setup_logging(name="test_logger_3", debug=True)
        assert logger.level == logging.DEBUG

    def test_has_stream_handler(self):
        """Test that logger has a StreamHandler."""
        logger = setup_logging(name="test_logger_4")
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_handler_level_matches_logger(self):
        """Test handler level matches logger level."""
        logger = setup_logging(name="test_logger_5", debug=True)
        assert logger.handlers[0].level == logging.DEBUG

        logger2 = setup_logging(name="test_logger_6", debug=False)
        assert logger2.handlers[0].level == logging.INFO

    def test_clears_existing_handlers(self):
        """Test that existing handlers are cleared on subsequent calls."""
        logger = setup_logging(name="test_logger_7")
        assert len(logger.handlers) == 1

        # Call again - should still only have 1 handler
        logger = setup_logging(name="test_logger_7")
        assert len(logger.handlers) == 1

    def test_custom_format(self):
        """Test custom log format is applied."""
        custom_format = "%(message)s"
        logger = setup_logging(name="test_logger_8", log_format=custom_format)
        formatter = logger.handlers[0].formatter
        assert formatter._fmt == custom_format

    def test_custom_date_format(self):
        """Test custom date format is applied."""
        custom_date_format = "%Y/%m/%d"
        logger = setup_logging(name="test_logger_9", date_format=custom_date_format)
        formatter = logger.handlers[0].formatter
        assert formatter.datefmt == custom_date_format

    def test_default_format_constants(self):
        """Test that default format constants are used."""
        logger = setup_logging(name="test_logger_10")
        formatter = logger.handlers[0].formatter
        assert formatter._fmt == LOG_FORMAT
        assert formatter.datefmt == DATE_FORMAT

    def test_quiet_level_true(self):
        """Test log level is WARNING when quiet=True."""
        logger = setup_logging(name="test_logger_quiet_1", quiet=True)
        assert logger.level == logging.WARNING

    def test_debug_overrides_quiet(self):
        """Test debug=True overrides quiet=True to DEBUG level."""
        logger = setup_logging(name="test_logger_quiet_2", debug=True, quiet=True)
        assert logger.level == logging.DEBUG

    def test_default_quiet_is_false(self):
        """Test quiet defaults to False (INFO level)."""
        logger = setup_logging(name="test_logger_quiet_3")
        assert logger.level == logging.INFO

    def test_handler_level_matches_quiet(self):
        """Test handler level matches WARNING when quiet=True."""
        logger = setup_logging(name="test_logger_quiet_4", quiet=True)
        assert logger.handlers[0].level == logging.WARNING

    def test_quiet_mode_suppresses_info(self):
        """Test INFO messages are filtered in quiet mode."""
        logger = setup_logging(name="test_logger_quiet_5", quiet=True)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.WARNING)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.handlers = [handler]

        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        output = stream.getvalue()
        assert "Info message" not in output
        assert "Warning message" in output
        assert "Error message" in output


class TestGetLogger:
    """Tests for get_logger function."""

    def test_returns_default_logger_when_no_name(self):
        """Test returns default ap_common logger when name is None."""
        logger = get_logger()
        assert logger.name == "ap_common"

    def test_returns_named_logger(self):
        """Test returns logger with specified name."""
        logger = get_logger(name="my_module")
        assert logger.name == "my_module"

    def test_caches_default_logger(self):
        """Test that the default logger is cached and reused."""
        # Reset the module-level _logger to ensure fresh start
        import ap_common.logging_config as lc

        lc._logger = None

        logger1 = get_logger()
        logger2 = get_logger()
        assert logger1 is logger2

    def test_creates_default_logger_if_not_exists(self):
        """Test that default logger is created if it doesn't exist."""
        import ap_common.logging_config as lc

        lc._logger = None

        logger = get_logger()
        assert logger is not None
        assert logger.name == "ap_common"

    def test_named_logger_is_standard_python_logger(self):
        """Test that named loggers are standard Python loggers."""
        logger = get_logger(name="test_named")
        assert logger is logging.getLogger("test_named")


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logger_outputs_message(self, capsys):
        """Test that logger actually outputs messages."""
        logger = setup_logging(name="test_output_logger")

        # Capture the output by adding a handler with StringIO
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.handlers = [handler]

        logger.info("Test message")

        output = stream.getvalue()
        assert "Test message" in output

    def test_debug_messages_not_shown_at_info_level(self):
        """Test that debug messages are not shown when level is INFO."""
        logger = setup_logging(name="test_debug_filter", debug=False)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.handlers = [handler]

        logger.debug("Debug message")
        logger.info("Info message")

        output = stream.getvalue()
        assert "Debug message" not in output
        assert "Info message" in output

    def test_debug_messages_shown_at_debug_level(self):
        """Test that debug messages are shown when level is DEBUG."""
        logger = setup_logging(name="test_debug_show", debug=True)

        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.handlers = [handler]

        logger.debug("Debug message")

        output = stream.getvalue()
        assert "Debug message" in output
