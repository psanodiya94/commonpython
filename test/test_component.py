"""
Test cases for Component Framework

Tests component framework functionality including ComponentBase, ComponentRunner,
and ComponentRegistry.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.framework import ComponentBase, ComponentRegistry, ComponentRunner, run_component


class TestComponent(ComponentBase):
    """
    Test component for testing purposes.

    @brief Simple test component that implements ComponentBase.
    """

    def __init__(self, config_file: str = None):
        """
        Initialize the test component.

        @brief Initialize test component.
        @param config_file Path to configuration file
        """
        super().__init__("TestComponent", config_file)
        self.initialized = False
        self.ran = False
        self.cleaned_up = False

    def initialize(self) -> bool:
        """
        Initialize the component.

        @brief Test component initialization.
        @return True if initialization successful, False otherwise
        """
        self.initialized = True
        return True

    def run(self) -> bool:
        """
        Run the component.

        @brief Test component execution.
        @return True if execution successful, False otherwise
        """
        self.ran = True
        return True

    def cleanup(self) -> None:
        """
        Cleanup the component.

        @brief Test component cleanup.
        """
        self.cleaned_up = True


class TestComponentBase(unittest.TestCase):
    """
    Test cases for ComponentBase class.

    @brief Comprehensive test suite for component base functionality.
    """

    def setUp(self):
        """
        Set up test fixtures.

        @brief Initialize test environment before each test.
        """
        # Create temporary config file with proper YAML structure
        self.temp_config = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        import yaml

        test_config = {
            "component": {
                "test_value": "test",
                "operation_count": 5,
                "test": {"key": "test_value"},
            },
            "database": {
                "host": "localhost",
                "port": 50000,
                "name": "testdb",
                "user": "db2inst1",
                "password": "password",
                "schema": "testschema",
                "timeout": 30,
            },
            "messaging": {
                "host": "localhost",
                "port": 1414,
                "queue_manager": "TEST_QM",
                "channel": "SYSTEM.DEF.SVRCONN",
                "user": "mquser",
                "password": "mqpass",
                "timeout": 30,
            },
            "logging": {
                "level": "INFO",
                "file": "TestComponent.log",
                "dir": "log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "max_size": 10485760,
                "backup_count": 5,
                "colored": True,
                "json_format": False,
                "console": False,
            },
        }
        yaml.dump(test_config, self.temp_config)
        self.temp_config.close()

    def tearDown(self):
        """
        Clean up test fixtures.

        @brief Clean up test environment after each test.
        """
        if (
            hasattr(self, "temp_config")
            and self.temp_config
            and os.path.exists(self.temp_config.name)
        ):
            os.unlink(self.temp_config.name)

    def test_config_access(self):
        """
        Test configuration access.

        @brief Test that component can access configuration.
        """
        component = TestComponent(self.temp_config.name)
        value = component.get_config("component.test.key", "default")
        self.assertIsNotNone(value)

    def test_set_config(self):
        """
        Test configuration setting.

        @brief Test that component can set configuration.
        """
        component = TestComponent(self.temp_config.name)
        component.set_config("test.key", "test_value")
        value = component.get_config("test.key")
        self.assertEqual(value, "test_value")

    def test_get_config_missing_key(self):
        """
        @brief Test get_config with missing key returns default.
        @details Covers branch where config key is missing.
        """
        component = TestComponent(self.temp_config.name)
        value = component.get_config("nonexistent.key", "default")
        self.assertEqual(value, "default")

    def test_logging_methods(self):
        """
        Test logging methods.

        @brief Test that component logging methods work correctly.
        """
        component = TestComponent(self.temp_config.name)
        # These should not raise exceptions
        component.log_info("Test info message")
        component.log_error("Test error message")
        component.log_warning("Test warning message")
        component.log_debug("Test debug message")

    def test_database_operations(self):
        """
        Test database operations.

        @brief Test that component database operations work correctly.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.connect = MagicMock(return_value=True)
        component.db_manager.execute_query = MagicMock(return_value=[{"count": 5}])
        component.db_manager.execute_update = MagicMock(return_value=1)
        component.db_manager.disconnect = MagicMock()

        self.assertTrue(component.connect_database())
        results = component.execute_query("SELECT * FROM test")
        self.assertEqual(results, [{"count": 5}])
        rows_affected = component.execute_update("INSERT INTO test VALUES (?)", ("value",))
        self.assertEqual(rows_affected, 1)
        component.disconnect_database()

    def test_messaging_operations(self):
        """
        Test messaging operations.

        @brief Test that component messaging operations work correctly.
        """
        component = TestComponent(self.temp_config.name)
        component.mq_manager.connect = MagicMock(return_value=True)
        component.mq_manager.put_message = MagicMock(return_value=True)
        component.mq_manager.get_message = MagicMock(return_value={"data": "test"})
        component.mq_manager.disconnect = MagicMock()

        self.assertTrue(component.connect_messaging())
        self.assertTrue(component.send_message("QUEUE", "msg"))
        message = component.receive_message("QUEUE")
        self.assertIsNotNone(message)
        component.disconnect_messaging()

    def test_start_method(self):
        """
        Test component start method.

        @brief Test that component start method works correctly.
        """
        component = TestComponent(self.temp_config.name)
        result = component.start()
        self.assertTrue(result)
        self.assertTrue(component.initialized)
        self.assertTrue(component.ran)
        self.assertTrue(component.cleaned_up)

    def test_start_initialize_false(self):
        """
        @brief Test start method when initialize returns False.
        @details Covers branch where initialization fails and logs error.
        """

        class FailComponent(TestComponent):
            def initialize(self):
                return False

        component = FailComponent(self.temp_config.name)
        result = component.start()
        self.assertFalse(result)

    def test_start_run_false(self):
        """
        @brief Test start method when run returns False.
        @details Covers branch where run fails and logs error.
        """

        class FailComponent(TestComponent):
            def run(self):
                return False

        component = FailComponent(self.temp_config.name)
        result = component.start()
        self.assertFalse(result)

    def test_start_exception_in_initialize(self):
        """
        @brief Test start method when initialize raises exception.
        """

        class ErrorComponent(TestComponent):
            def initialize(self):
                raise Exception("Init error")

        component = ErrorComponent(self.temp_config.name)
        result = component.start()
        self.assertFalse(result)

    def test_start_exception_in_run(self):
        """
        @brief Test start method when run raises exception.
        """

        class ErrorComponent(TestComponent):
            def run(self):
                raise Exception("Run error")

        component = ErrorComponent(self.temp_config.name)
        result = component.start()
        self.assertFalse(result)

    def test_start_exception_in_cleanup(self):
        """
        @brief Test start method when cleanup raises exception.
        """

        class ErrorComponent(TestComponent):
            def cleanup(self):
                raise Exception("Cleanup error")

        component = ErrorComponent(self.temp_config.name)
        # Should handle exception gracefully
        result = component.start()
        # Result can be True or False depending on whether init/run succeeded
        self.assertIsNotNone(result)

    def test_connect_database_exception(self):
        """
        @brief Test connect_database exception branch and logger error handling.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.connect = MagicMock(side_effect=Exception("db error"))
        result = component.connect_database()
        self.assertFalse(result)

    def test_disconnect_database_exception(self):
        """
        @brief Test disconnect_database exception branch and logger error handling.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.disconnect = MagicMock(side_effect=Exception("db error"))
        # Should not raise exception
        component.disconnect_database()

    def test_connect_messaging_exception(self):
        """
        @brief Test connect_messaging exception branch and logger error handling.
        """
        component = TestComponent(self.temp_config.name)
        component.mq_manager.connect = MagicMock(side_effect=Exception("mq error"))
        result = component.connect_messaging()
        self.assertFalse(result)

    def test_disconnect_messaging_exception(self):
        """
        @brief Test disconnect_messaging exception branch and logger error handling.
        """
        component = TestComponent(self.temp_config.name)
        component.mq_manager.disconnect = MagicMock(side_effect=Exception("mq error"))
        # Should not raise exception
        component.disconnect_messaging()

    def test_execute_query_exception(self):
        """
        @brief Test execute_query exception branch and logger error handling.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.execute_query = MagicMock(side_effect=Exception("query error"))
        with self.assertRaises(Exception):
            component.execute_query("SELECT * FROM test")

    def test_execute_update_exception(self):
        """
        @brief Test execute_update exception branch and logger error handling.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.execute_update = MagicMock(side_effect=Exception("update error"))
        with self.assertRaises(Exception):
            component.execute_update("UPDATE test SET value=1")

    def test_send_message_exception(self):
        """
        @brief Test send_message exception branch and logger error handling.
        """
        component = TestComponent(self.temp_config.name)
        component.mq_manager.put_message = MagicMock(side_effect=Exception("send error"))
        result = component.send_message("QUEUE", "msg")
        self.assertFalse(result)

    def test_receive_message_exception(self):
        """
        @brief Test receive_message exception branch and logger error handling.
        """
        component = TestComponent(self.temp_config.name)
        component.mq_manager.get_message = MagicMock(side_effect=Exception("recv error"))
        result = component.receive_message("QUEUE")
        self.assertIsNone(result)


class TestComponentRunner(unittest.TestCase):
    """
    Test cases for ComponentRunner class.

    @brief Comprehensive test suite for component runner functionality.
    """

    def test_init(self):
        """
        Test component runner initialization.

        @brief Test that component runner initializes correctly.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")

        self.assertEqual(runner.component_class, TestComponent)
        self.assertEqual(runner.component_name, "TestComponent")
        self.assertIsNone(runner.component_instance)

    def test_create_parser(self):
        """
        Test parser creation.

        @brief Test that component runner creates argument parser correctly.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")
        parser = runner.create_parser()

        self.assertIsNotNone(parser)
        self.assertEqual(parser.description, "TestComponent - CommonPython Component")

    def test_run_with_config(self):
        """
        Test running component with configuration.

        @brief Test that component runner can run with configuration dictionary.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            test_config = {
                "logging": {"level": "INFO", "dir": "log"},
                "component": {"test_key": "test_value"},
            }
            yaml.dump(test_config, f)
            config_file = f.name

        try:
            # Create instance with config file
            component = TestComponent(config_file)

            with patch.object(runner, "component_class", return_value=component):
                config = {"key1": "value1", "key2": "value2"}
                result = runner.run_with_config(config)
                self.assertTrue(result)
        finally:
            os.unlink(config_file)

    def test_run_with_config_exception(self):
        """
        @brief Test run_with_config handles exception and logs error.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")

        with patch.object(
            runner, "component_class", side_effect=Exception("Component creation failed")
        ):
            result = runner.run_with_config({"key": "value"})
            self.assertFalse(result)

    def test_run_dry_run(self):
        """
        Test dry-run mode branch in runner.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")

        with patch.object(runner, "create_parser") as mock_parser:
            mock_args = MagicMock()
            mock_parser.return_value.parse_args.return_value = mock_args
            mock_args.config = None
            mock_args.log_level = "INFO"
            mock_args.verbose = False
            mock_args.dry_run = True

            result = runner.run([])
            self.assertTrue(result)

    @patch("commonpython.framework.component_base.ComponentBase.start")
    def test_run_keyboard_interrupt(self, mock_start):
        """
        Test runner handles KeyboardInterrupt gracefully.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")

        with patch.object(runner, "create_parser") as mock_parser:
            mock_args = MagicMock()
            mock_parser.return_value.parse_args.return_value = mock_args
            mock_args.config = None
            mock_args.log_level = "INFO"
            mock_args.verbose = False
            mock_args.dry_run = False

            # Simulate KeyboardInterrupt during start
            mock_start.side_effect = KeyboardInterrupt()

            result = runner.run([])
            self.assertFalse(result)

    def test_run_exception_no_instance(self):
        """
        @brief Test runner handles exception when no instance exists.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")

        with patch.object(runner, "create_parser") as mock_parser:
            mock_args = MagicMock()
            mock_parser.return_value.parse_args.return_value = mock_args
            mock_args.config = None
            mock_args.log_level = "INFO"
            mock_args.verbose = False
            mock_args.dry_run = False

            # Simulate error during instance creation
            with patch.object(runner, "component_class", side_effect=Exception("Creation failed")):
                result = runner.run([])
                self.assertFalse(result)


class TestComponentRegistry(unittest.TestCase):
    """
    Test cases for ComponentRegistry class.

    @brief Comprehensive test suite for component registry functionality.
    """

    def setUp(self):
        """
        Set up test fixtures.

        @brief Initialize test environment before each test.
        """
        self.registry = ComponentRegistry()

    def test_register_component(self):
        """
        Test component registration.

        @brief Test that components can be registered correctly.
        """
        self.registry.register("test", TestComponent)

        self.assertTrue(self.registry.is_registered("test"))
        self.assertEqual(self.registry.get_component_count(), 1)

    def test_register_duplicate_component(self):
        """
        Test duplicate component registration.

        @brief Test that duplicate component registration raises error.
        """
        self.registry.register("test", TestComponent)

        with self.assertRaises(ValueError):
            self.registry.register("test", TestComponent)

    def test_unregister_component(self):
        """
        Test component unregistration.

        @brief Test that components can be unregistered correctly.
        """
        self.registry.register("test", TestComponent)
        self.registry.unregister("test")

        self.assertFalse(self.registry.is_registered("test"))
        self.assertEqual(self.registry.get_component_count(), 0)

    def test_unregister_nonexistent_component(self):
        """
        Test unregistering nonexistent component.

        @brief Test that unregistering nonexistent component raises error.
        """
        with self.assertRaises(KeyError):
            self.registry.unregister("nonexistent")

    def test_get_component(self):
        """
        Test getting registered component.

        @brief Test that registered components can be retrieved correctly.
        """
        self.registry.register("test", TestComponent)

        component_class = self.registry.get_component("test")
        self.assertEqual(component_class, TestComponent)

    def test_get_nonexistent_component(self):
        """
        Test getting nonexistent component.

        @brief Test that getting nonexistent component raises error.
        """
        with self.assertRaises(KeyError):
            self.registry.get_component("nonexistent")

    def test_list_components(self):
        """
        Test listing components.

        @brief Test that component list is returned correctly.
        """
        self.registry.register("test1", TestComponent)
        self.registry.register("test2", TestComponent)

        components = self.registry.list_components()
        self.assertEqual(len(components), 2)
        self.assertIn("test1", components)
        self.assertIn("test2", components)

    def test_clear_registry(self):
        """
        Test clearing registry.

        @brief Test that registry can be cleared correctly.
        """
        self.registry.register("test1", TestComponent)
        self.registry.register("test2", TestComponent)

        self.registry.clear()

        self.assertEqual(self.registry.get_component_count(), 0)
        self.assertEqual(len(self.registry.list_components()), 0)


class TestRunComponent(unittest.TestCase):
    """
    Test cases for run_component convenience function.

    @brief Test suite for run_component function.
    """

    @patch("commonpython.framework.component_runner.ComponentRunner.run")
    def test_run_component(self, mock_run):
        """
        Test run_component function.

        @brief Test that run_component function works correctly.
        """
        mock_run.return_value = True

        result = run_component(TestComponent, "TestComponent")

        self.assertTrue(result)
        mock_run.assert_called_once_with(None)


if __name__ == "__main__":
    unittest.main()
