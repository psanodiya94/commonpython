"""
Comprehensive Tests for Custom Exceptions

Test suite for all custom exception classes to ensure proper
error handling and exception mapping functionality.
"""

import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.exceptions import (  # noqa: E402
    EXCEPTION_MAP,
    AdapterError,
    AdapterInitializationError,
    AdapterNotAvailableError,
    CLICommandError,
    CLIError,
    CommonPythonError,
    ComponentError,
    ComponentExecutionError,
    ComponentInitializationError,
    ConfigFileNotFoundError,
    ConfigurationError,
    ConfigValidationError,
    DatabaseConnectionError,
    DatabaseError,
    DatabaseQueryError,
    DatabaseTimeoutError,
    DatabaseTransactionError,
    InvalidParameterError,
    LoggingError,
    MessageReceiveError,
    MessageSendError,
    MessagingConnectionError,
    MessagingError,
    MessagingTimeoutError,
    MissingParameterError,
    QueueNotFoundError,
    TimeoutError,
    ValidationError,
    map_exception,
)


class TestCommonPythonError(unittest.TestCase):
    """Test suite for base CommonPythonError"""

    def test_exception_with_message_only(self):
        """Test exception with message only"""
        exc = CommonPythonError("Test error")
        self.assertEqual(exc.message, "Test error")
        self.assertEqual(exc.details, {})
        self.assertEqual(str(exc), "Test error")

    def test_exception_with_message_and_details(self):
        """Test exception with message and details"""
        details = {"code": 500, "component": "test"}
        exc = CommonPythonError("Test error", details)
        self.assertEqual(exc.message, "Test error")
        self.assertEqual(exc.details, details)
        self.assertIn("code=500", str(exc))
        self.assertIn("component=test", str(exc))

    def test_exception_with_empty_details(self):
        """Test exception with explicit empty details"""
        exc = CommonPythonError("Test error", {})
        self.assertEqual(exc.details, {})
        self.assertEqual(str(exc), "Test error")

    def test_exception_string_representation_with_details(self):
        """Test string representation includes details"""
        exc = CommonPythonError("Error occurred", {"user": "admin", "action": "delete"})
        str_repr = str(exc)
        self.assertIn("Error occurred", str_repr)
        self.assertIn("user=admin", str_repr)
        self.assertIn("action=delete", str_repr)

    def test_exception_inheritance(self):
        """Test that CommonPythonError inherits from Exception"""
        exc = CommonPythonError("Test")
        self.assertIsInstance(exc, Exception)

    def test_exception_can_be_raised_and_caught(self):
        """Test exception can be raised and caught"""
        with self.assertRaises(CommonPythonError) as context:
            raise CommonPythonError("Test exception")
        self.assertEqual(str(context.exception), "Test exception")


class TestConfigurationExceptions(unittest.TestCase):
    """Test suite for configuration-related exceptions"""

    def test_configuration_error(self):
        """Test ConfigurationError"""
        exc = ConfigurationError("Config error")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "Config error")

    def test_config_file_not_found_error(self):
        """Test ConfigFileNotFoundError"""
        exc = ConfigFileNotFoundError("File not found", {"file": "config.yaml"})
        self.assertIsInstance(exc, ConfigurationError)
        self.assertIn("File not found", str(exc))

    def test_config_validation_error(self):
        """Test ConfigValidationError"""
        exc = ConfigValidationError("Validation failed")
        self.assertIsInstance(exc, ConfigurationError)
        self.assertEqual(str(exc), "Validation failed")


class TestDatabaseExceptions(unittest.TestCase):
    """Test suite for database-related exceptions"""

    def test_database_error(self):
        """Test DatabaseError"""
        exc = DatabaseError("DB error")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "DB error")

    def test_database_connection_error(self):
        """Test DatabaseConnectionError"""
        exc = DatabaseConnectionError("Connection failed", {"host": "localhost"})
        self.assertIsInstance(exc, DatabaseError)
        self.assertIn("Connection failed", str(exc))

    def test_database_query_error(self):
        """Test DatabaseQueryError"""
        exc = DatabaseQueryError("Query failed")
        self.assertIsInstance(exc, DatabaseError)
        self.assertEqual(str(exc), "Query failed")

    def test_database_transaction_error(self):
        """Test DatabaseTransactionError"""
        exc = DatabaseTransactionError("Transaction failed")
        self.assertIsInstance(exc, DatabaseError)
        self.assertEqual(str(exc), "Transaction failed")


class TestMessagingExceptions(unittest.TestCase):
    """Test suite for messaging-related exceptions"""

    def test_messaging_error(self):
        """Test MessagingError"""
        exc = MessagingError("MQ error")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "MQ error")

    def test_messaging_connection_error(self):
        """Test MessagingConnectionError"""
        exc = MessagingConnectionError("Connection failed", {"queue_manager": "QM1"})
        self.assertIsInstance(exc, MessagingError)
        self.assertIn("Connection failed", str(exc))

    def test_message_send_error(self):
        """Test MessageSendError"""
        exc = MessageSendError("Send failed")
        self.assertIsInstance(exc, MessagingError)
        self.assertEqual(str(exc), "Send failed")

    def test_message_receive_error(self):
        """Test MessageReceiveError"""
        exc = MessageReceiveError("Receive failed")
        self.assertIsInstance(exc, MessagingError)
        self.assertEqual(str(exc), "Receive failed")

    def test_queue_not_found_error(self):
        """Test QueueNotFoundError"""
        exc = QueueNotFoundError("Queue not found", {"queue": "TEST.QUEUE"})
        self.assertIsInstance(exc, MessagingError)
        self.assertIn("Queue not found", str(exc))


class TestLoggingExceptions(unittest.TestCase):
    """Test suite for logging-related exceptions"""

    def test_logging_error(self):
        """Test LoggingError"""
        exc = LoggingError("Logging error")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "Logging error")


class TestAdapterExceptions(unittest.TestCase):
    """Test suite for adapter-related exceptions"""

    def test_adapter_error(self):
        """Test AdapterError"""
        exc = AdapterError("Adapter error")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "Adapter error")

    def test_adapter_not_available_error(self):
        """Test AdapterNotAvailableError"""
        exc = AdapterNotAvailableError("Adapter not available", {"adapter": "library"})
        self.assertIsInstance(exc, AdapterError)
        self.assertIn("Adapter not available", str(exc))

    def test_adapter_initialization_error(self):
        """Test AdapterInitializationError"""
        exc = AdapterInitializationError("Init failed")
        self.assertIsInstance(exc, AdapterError)
        self.assertEqual(str(exc), "Init failed")


class TestComponentExceptions(unittest.TestCase):
    """Test suite for component-related exceptions"""

    def test_component_error(self):
        """Test ComponentError"""
        exc = ComponentError("Component error")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "Component error")

    def test_component_initialization_error(self):
        """Test ComponentInitializationError"""
        exc = ComponentInitializationError("Init failed", {"component": "TestComponent"})
        self.assertIsInstance(exc, ComponentError)
        self.assertIn("Init failed", str(exc))

    def test_component_execution_error(self):
        """Test ComponentExecutionError"""
        exc = ComponentExecutionError("Execution failed")
        self.assertIsInstance(exc, ComponentError)
        self.assertEqual(str(exc), "Execution failed")


class TestCLIExceptions(unittest.TestCase):
    """Test suite for CLI-related exceptions"""

    def test_cli_error(self):
        """Test CLIError"""
        exc = CLIError("CLI error")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "CLI error")

    def test_cli_command_error(self):
        """Test CLICommandError"""
        exc = CLICommandError("Command failed", {"command": "test"})
        self.assertIsInstance(exc, CLIError)
        self.assertIn("Command failed", str(exc))


class TestValidationExceptions(unittest.TestCase):
    """Test suite for validation-related exceptions"""

    def test_validation_error(self):
        """Test ValidationError"""
        exc = ValidationError("Validation error")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "Validation error")

    def test_invalid_parameter_error(self):
        """Test InvalidParameterError"""
        exc = InvalidParameterError("Invalid param", {"param": "timeout"})
        self.assertIsInstance(exc, ValidationError)
        self.assertIn("Invalid param", str(exc))

    def test_missing_parameter_error(self):
        """Test MissingParameterError"""
        exc = MissingParameterError("Missing param")
        self.assertIsInstance(exc, ValidationError)
        self.assertEqual(str(exc), "Missing param")


class TestTimeoutExceptions(unittest.TestCase):
    """Test suite for timeout-related exceptions"""

    def test_timeout_error(self):
        """Test TimeoutError"""
        exc = TimeoutError("Timeout")
        self.assertIsInstance(exc, CommonPythonError)
        self.assertEqual(str(exc), "Timeout")

    def test_database_timeout_error(self):
        """Test DatabaseTimeoutError"""
        exc = DatabaseTimeoutError("DB timeout", {"timeout": 30})
        self.assertIsInstance(exc, TimeoutError)
        self.assertIn("DB timeout", str(exc))

    def test_messaging_timeout_error(self):
        """Test MessagingTimeoutError"""
        exc = MessagingTimeoutError("MQ timeout")
        self.assertIsInstance(exc, TimeoutError)
        self.assertEqual(str(exc), "MQ timeout")


class TestExceptionMapping(unittest.TestCase):
    """Test suite for exception mapping functionality"""

    def test_map_file_not_found_error(self):
        """Test mapping FileNotFoundError"""
        original = FileNotFoundError("File not found")
        mapped = map_exception(original)
        self.assertIsInstance(mapped, ConfigFileNotFoundError)
        self.assertIn("File not found", str(mapped))

    def test_map_file_not_found_error_with_custom_message(self):
        """Test mapping FileNotFoundError with custom message"""
        original = FileNotFoundError("File not found")
        mapped = map_exception(original, "Custom config file error")
        self.assertIsInstance(mapped, ConfigFileNotFoundError)
        self.assertEqual(mapped.message, "Custom config file error")
        self.assertIn("original_error", mapped.details)

    def test_map_key_error(self):
        """Test mapping KeyError"""
        original = KeyError("missing_key")
        mapped = map_exception(original)
        self.assertIsInstance(mapped, ConfigurationError)

    def test_map_value_error(self):
        """Test mapping ValueError"""
        original = ValueError("Invalid value")
        mapped = map_exception(original)
        self.assertIsInstance(mapped, ValidationError)
        self.assertIn("Invalid value", str(mapped))

    def test_map_connection_error(self):
        """Test mapping ConnectionError"""
        original = ConnectionError("Connection failed")
        mapped = map_exception(original)
        self.assertIsInstance(mapped, DatabaseConnectionError)

    def test_map_unknown_exception(self):
        """Test mapping unknown exception type"""
        original = RuntimeError("Runtime error")
        mapped = map_exception(original)
        self.assertIsInstance(mapped, CommonPythonError)
        self.assertIn("Runtime error", str(mapped))

    def test_map_exception_preserves_original_error(self):
        """Test that mapped exception preserves original error in details"""
        original = ValueError("Test error")
        mapped = map_exception(original, "Mapped error")
        self.assertIn("original_error", mapped.details)
        self.assertIn("Test error", mapped.details["original_error"])

    def test_exception_map_contains_expected_keys(self):
        """Test EXCEPTION_MAP contains expected mappings"""
        self.assertIn("FileNotFoundError", EXCEPTION_MAP)
        self.assertIn("KeyError", EXCEPTION_MAP)
        self.assertIn("ValueError", EXCEPTION_MAP)
        self.assertIn("ConnectionError", EXCEPTION_MAP)

    def test_exception_map_values_are_exception_classes(self):
        """Test EXCEPTION_MAP values are exception classes"""
        for _key, value in EXCEPTION_MAP.items():
            self.assertTrue(issubclass(value, CommonPythonError))


if __name__ == "__main__":
    unittest.main()
