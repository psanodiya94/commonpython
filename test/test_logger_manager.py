"""
Test cases for LoggerManager

Tests logging functionality using only standard Python modules.
"""

import json
import logging
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.logging.logger_manager import ColoredFormatter, JSONFormatter, LoggerManager


def safe_remove(filepath, retries=5, delay=0.2):
    """Try to remove a file with retries to avoid Windows PermissionError."""
    for _ in range(retries):
        try:
            os.remove(filepath)
            return
        except PermissionError:
            time.sleep(delay)
    # Last attempt
    try:
        os.remove(filepath)
    except PermissionError:
        if sys.platform.startswith("win"):
            pass  # Skip deletion on Windows if still locked
        else:
            raise


class TestLoggerManager(unittest.TestCase):
    """
    Test cases for LoggerManager class.

    @brief Comprehensive test suite for logging functionality.
    """

    def setUp(self):
        """
        Set up test fixtures.

        @brief Initialize test environment before each test.
        """
        # Clear any existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    def test_init_default(self):
        """
        Test LoggerManager initialization with default parameters.

        @brief Test that LoggerManager initializes correctly with default settings.
        """
        config = {"dir": "log"}
        logger_manager = LoggerManager(config=config)
        self.assertIsInstance(logger_manager, LoggerManager)
        self.assertEqual(logger_manager.name, "commonpython")
        self.assertEqual(logger_manager.config, config)

    def test_init_with_name(self):
        """
        Test LoggerManager initialization with custom name.

        @brief Test LoggerManager initialization with custom logger name.
        """
        config = {"dir": "log"}
        logger_manager = LoggerManager("test_logger", config)
        self.assertEqual(logger_manager.name, "test_logger")

    def test_init_with_config(self):
        """
        Test LoggerManager initialization with configuration.

        @brief Test LoggerManager initialization with custom configuration.
        """
        config = {"level": "DEBUG", "dir": "log", "file": "test.log"}
        logger_manager = LoggerManager("test", config)
        self.assertEqual(logger_manager.config, config)
        handlers = logger_manager.logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger_manager.logger.removeHandler(handler)
        import gc

        gc.collect()
        safe_remove(os.path.join("log", "test.log"))

    def test_get_logger(self):
        """
        Test getting logger instance.

        @brief Test retrieval of logger instance.
        """
        config = {"dir": "log"}
        logger_manager = LoggerManager("test", config)
        logger = logger_manager.get_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test")

    def test_get_logger_with_name(self):
        """
        Test getting logger instance with custom name.

        @brief Test retrieval of logger instance with custom name.
        """
        config = {"dir": "log"}
        logger_manager = LoggerManager("test", config)
        logger = logger_manager.get_logger("custom")
        self.assertEqual(logger.name, "custom")

    def test_set_level(self):
        """
        Test setting logging level.

        @brief Test setting logging level for all handlers.
        """
        config = {"dir": "log"}
        logger_manager = LoggerManager("test", config)
        logger_manager.set_level("DEBUG")
        self.assertEqual(logger_manager.logger.level, logging.DEBUG)

    def test_set_level_invalid(self):
        """
        Test set_level with invalid level.
        """
        config = {"dir": "log"}
        logger_manager = LoggerManager("test", config)
        # Should not raise, but fallback to default
        logger_manager.set_level("NOTALEVEL")

    def test_json_formatter_error(self):
        """
        @brief Test JSONFormatter with unserializable object (should fallback to str).
        """
        import logging

        formatter = JSONFormatter()
        # Create a real LogRecord with unserializable msg
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=object(),
            args=(),
            exc_info=None,
        )
        try:
            formatter.format(record)
        except Exception:
            self.fail("JSONFormatter raised unexpectedly!")

    def test_colored_formatter_error(self):
        """
        Test ColoredFormatter with missing color.
        """
        formatter = ColoredFormatter()
        record = MagicMock()
        record.levelname = "NOTALEVEL"
        record.getMessage.return_value = "msg"
        # Should not raise
        try:
            formatter.format(record)
        except Exception:
            self.fail("ColoredFormatter raised unexpectedly!")

    def test_log_function_call(self):
        """
        Test logging function calls.

        @brief Test logging of function call details.
        """
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_file = f.name
        config = {"file": temp_file, "json_format": True}
        logger_manager = LoggerManager("test", config)
        logger_manager.log_function_call(
            "test_function",
            func_args=(1, 2),
            func_kwargs={"key": "value"},
            result="success",
            duration=0.5,
        )
        handlers = logger_manager.logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger_manager.logger.removeHandler(handler)
        import gc

        gc.collect()
        with open(temp_file) as f:
            log_content = f.read()
            self.assertIn("function_call", log_content)
            self.assertIn("test_function", log_content)
        safe_remove(temp_file)

    def test_log_database_operation(self):
        """
        Test logging database operations.

        @brief Test logging of database operation details.
        """
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_file = f.name
        config = {"file": temp_file, "json_format": True}
        logger_manager = LoggerManager("test", config)
        logger_manager.log_database_operation(
            "SELECT", table="users", query="SELECT * FROM users", duration=0.1, rows_affected=5
        )
        handlers = logger_manager.logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger_manager.logger.removeHandler(handler)
        import gc

        gc.collect()
        with open(temp_file) as f:
            log_content = f.read()
            self.assertIn("database_operation", log_content)
            self.assertIn("SELECT", log_content)
        safe_remove(temp_file)

    def test_log_mq_operation(self):
        """
        Test logging MQ operations.

        @brief Test logging of MQ operation details.
        """
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_file = f.name
        config = {"file": temp_file, "json_format": True}
        logger_manager = LoggerManager("test", config)
        logger_manager.log_mq_operation(
            "PUT", queue="test_queue", message_id="msg123", message_size=100, duration=0.05
        )
        handlers = logger_manager.logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger_manager.logger.removeHandler(handler)
        import gc

        gc.collect()
        with open(temp_file) as f:
            log_content = f.read()
            self.assertIn("mq_operation", log_content)
            self.assertIn("PUT", log_content)
        safe_remove(temp_file)


class TestJSONFormatter(unittest.TestCase):
    """
    Test cases for JSONFormatter class.

    @brief Test suite for JSON formatter functionality.
    """

    def test_format_basic(self):
        """
        Test basic JSON formatting.

        @brief Test that JSONFormatter formats log records correctly.
        """
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["logger"], "test")

    def test_format_with_exception(self):
        """
        Test JSON formatting with exception information.

        @brief Test that JSONFormatter handles exceptions correctly.
        """
        formatter = JSONFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Test message",
                args=(),
                exc_info=exc_info,
            )

            formatted = formatter.format(record)
            log_data = json.loads(formatted)

            self.assertIn("exception", log_data)
            self.assertIn("ValueError", log_data["exception"])


class TestColoredFormatter(unittest.TestCase):
    """
    Test cases for ColoredFormatter class.

    @brief Test suite for colored formatter functionality.
    """

    def test_format_with_colors(self):
        """
        Test colored formatting.

        @brief Test that ColoredFormatter adds color codes correctly.
        """
        formatter = ColoredFormatter("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Check that color codes are present
        self.assertIn("\033[32m", formatted)  # Green for INFO
        self.assertIn("\033[0m", formatted)  # Reset code

    def test_format_different_levels(self):
        """
        Test colored formatting for different log levels.

        @brief Test that different log levels get different colors.
        """
        formatter = ColoredFormatter("%(levelname)s - %(message)s")

        levels = [
            (logging.DEBUG, "\033[36m"),  # Cyan
            (logging.INFO, "\033[32m"),  # Green
            (logging.WARNING, "\033[33m"),  # Yellow
            (logging.ERROR, "\033[31m"),  # Red
            (logging.CRITICAL, "\033[35m"),  # Magenta
        ]

        for level, expected_color in levels:
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="test.py",
                lineno=1,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            formatted = formatter.format(record)
            self.assertIn(expected_color, formatted)
