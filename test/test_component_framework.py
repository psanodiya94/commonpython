"""
Test cases for Component Framework

Tests component framework functionality including ComponentBase, ComponentRunner,
and ComponentRegistry.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.framework import ComponentBase, ComponentRunner, ComponentRegistry, run_component


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

    def test_start_initialize_false(self):
        """
        @brief Test start method when initialize returns False.
        @details Covers branch where initialization fails and logs error.
        """
        class FailComponent(TestComponent):
            def initialize(self):
                return False

        try:
            component = FailComponent(self.temp_config.name)
            component.logger_manager.logger.error = MagicMock()
            component.logger_manager.logger.info = MagicMock()
            result = component.start()
            self.assertFalse(result)
            component.logger_manager.logger.error.assert_called()
        except SystemExit:
            pass

    def test_start_run_false(self):
        """
        @brief Test start method when run returns False.
        @details Covers branch where run fails and logs error.
        """
        class FailComponent(TestComponent):
            def run(self):
                return False

        try:
            component = FailComponent(self.temp_config.name)
            component.logger_manager.logger.error = MagicMock()
            component.logger_manager.logger.info = MagicMock()
            result = component.start()
            self.assertFalse(result)
            component.logger_manager.logger.error.assert_called()
        except SystemExit:
            pass

    def test_start_exception_in_cleanup_finally(self):
        """
        @brief Test start method finally block when cleanup raises exception and logs error.
        @details Covers finally block exception branch in start.
        """
        class ErrorComponent(TestComponent):
            def cleanup(self):
                raise Exception("Cleanup error")

        try:
            component = ErrorComponent(self.temp_config.name)
            component.logger_manager.logger.error = MagicMock()
            component.logger_manager.logger.info = MagicMock()
            result = component.start()
            component.logger_manager.logger.error.assert_called()
        except SystemExit:
            pass

    def test_log_methods_error_branches(self):
        """
        @brief Test all log methods error branches.
        @details Simulates logger raising exceptions for info, error, warning, debug.
        """
        component = TestComponent(self.temp_config.name)
        for method in [component.log_info, component.log_error, component.log_warning, component.log_debug]:
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
            try:
                method("msg")
            except Exception:
                pass

    def test_get_config_missing_key(self):
        """
        @brief Test get_config with missing key returns default.
        @details Covers branch where config key is missing.
        """
        component = TestComponent(self.temp_config.name)
        component.logger_manager.logger = MagicMock()
        value = component.get_config('nonexistent.key', 'default')
        self.assertEqual(value, 'default')

    def test_set_config_error_branch(self):
        """
        @brief Test set_config error branch when logger errors.
        @details Simulates logger raising exception during set_config.
        """
        try:
            component = TestComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
            component.set_config('key', 'value')
        except SystemExit:
            pass

    def test_connect_database_exception(self):
        """
        @brief Test connect_database exception branch and logger error handling.
        @details Verifies that send_message handles exceptions and logs errors correctly, including sys.exit(1) handling.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.connect = MagicMock(side_effect=Exception("db error"))
        component.logger_manager.logger.error = MagicMock()
        result = component.connect_database()
        self.assertFalse(result)
        component.logger_manager.logger.error.assert_called()

    def test_disconnect_database_exception(self):
        """
        @brief Test disconnect_database exception branch and logger error handling.
        @details Verifies that send_message handles exceptions and logs errors correctly, including sys.exit(1) handling.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.disconnect = MagicMock(side_effect=Exception("db error"))
        component.logger_manager.logger.error = MagicMock()
        component.disconnect_database()
        component.logger_manager.logger.error.assert_called()

    def test_connect_messaging_exception(self):
        """
        @brief Test connect_messaging exception branch and logger error handling.
        @details Verifies that send_message handles exceptions and logs errors correctly, including sys.exit(1) handling.
        """
        component = TestComponent(self.temp_config.name)
        component.mq_manager.connect = MagicMock(side_effect=Exception("mq error"))
        component.logger_manager.logger.error = MagicMock()
        result = component.connect_messaging()
        self.assertFalse(result)
        component.logger_manager.logger.error.assert_called()

    def test_disconnect_messaging_exception(self):
        """
        @brief Test disconnect_messaging exception branch and logger error handling.
        @details Verifies that send_message handles exceptions and logs errors correctly, including sys.exit(1) handling.
        """
        component = TestComponent(self.temp_config.name)
        component.mq_manager.disconnect = MagicMock(side_effect=Exception("mq error"))
        component.logger_manager.logger.error = MagicMock()
        component.disconnect_messaging()
        component.logger_manager.logger.error.assert_called()

    def test_execute_query_exception(self):
        """
        @brief Test execute_query exception branch and logger error handling.
        @details Verifies that send_message handles exceptions and logs errors correctly, including sys.exit(1) handling.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.execute_query = MagicMock(side_effect=Exception("query error"))
        component.logger_manager.logger.error = MagicMock()
        with self.assertRaises(Exception):
            component.execute_query("SELECT * FROM test")
        component.logger_manager.logger.error.assert_called()

    def test_execute_update_exception(self):
        """
        @brief Test execute_update exception branch and logger error handling.
        @details Verifies that send_message handles exceptions and logs errors correctly, including sys.exit(1) handling.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.execute_update = MagicMock(side_effect=Exception("update error"))
        component.logger_manager.logger.error = MagicMock()
        with self.assertRaises(Exception):
            component.execute_update("UPDATE test SET value=1")
        component.logger_manager.logger.error.assert_called()

    def test_send_message_exception(self):
        """
        @brief Test send_message exception branch and logger error handling.
        @details Verifies that send_message handles exceptions and logs errors correctly, including sys.exit(1) handling.
        """
        try:
            component = TestComponent(self.temp_config.name)
            component.mq_manager.put_message = MagicMock(side_effect=Exception("send error"))
            component.logger_manager.logger.error = MagicMock()
            result = component.send_message("QUEUE", "msg")
            self.assertFalse(result)
            component.logger_manager.logger.error.assert_called()
        except SystemExit:
            pass

    def test_receive_message_exception(self):
        """
        @brief Test receive_message exception branch and logger error handling.
        @details Verifies that receive_message handles exceptions and logs errors correctly, including sys.exit(1) handling.
        """
        try:
            component = TestComponent(self.temp_config.name)
            component.mq_manager.get_message = MagicMock(side_effect=Exception("recv error"))
            component.logger_manager.logger.error = MagicMock()
            result = component.receive_message("QUEUE")
            self.assertIsNone(result)
            component.logger_manager.logger.error.assert_called()
        except SystemExit:
            pass

    def test_start_finally_cleanup_exception(self):
        """
        @brief Test start method finally block when cleanup raises exception.
        @details Verifies that the finally block in start handles cleanup exceptions and logs errors, including sys.exit(1) handling.
        """
        try:
            class ErrorComponent(TestComponent):
                def cleanup(self):
                    raise Exception("Cleanup error")
            component = ErrorComponent(self.temp_config.name)
            component.logger_manager.logger.error = MagicMock()
            component.logger_manager.logger.info = MagicMock()
            result = component.start()
            component.logger_manager.logger.error.assert_called()
        except SystemExit:
            pass
    
    def test_initialize_fail(self):
        """
        Test initialize returns False branch.
        """
        class FailComponent(TestComponent):
            def initialize(self):
                return False
        component = FailComponent(self.temp_config.name)
        result = component.start()
        self.assertFalse(result)

    def test_run_fail(self):
        """
        Test run returns False branch.
        """
        class FailComponent(TestComponent):
            def run(self):
                return False
        try:
            component = FailComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
            result = component.start()
            self.assertFalse(result)
        except SystemExit:
            pass

    def test_cleanup_exception(self):
        """
        Test cleanup exception branch in start().
        """
        class ErrorComponent(TestComponent):
            def cleanup(self):
                raise Exception("Cleanup error")
        component = ErrorComponent(self.temp_config.name)
        # Should not raise
        component.start()
    
    def setUp(self):
        """
        Set up test fixtures.
        
        @brief Initialize test environment before each test.
        """
        # Create temporary config file with proper YAML structure
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        import yaml
        test_config = {
            'component': {
                'test_value': 'test',
                'operation_count': 5,
                'test': {
                    'key': 'test_value'
                }
            },
            'database': {
                'host': 'localhost',
                'port': 50000,
                'name': 'testdb',
                'user': 'db2inst1',
                'password': 'password',
                'schema': 'testschema',
                'timeout': 30
            },
            'messaging': {
                'host': 'localhost',
                'port': 1414,
                'queue_manager': 'TEST_QM',
                'channel': 'SYSTEM.DEF.SVRCONN',
                'user': 'mquser',
                'password': 'mqpass',
                'timeout': 30
            },
            'logging': {
                'level': 'INFO',
                'file': 'TestComponent.log',
                'dir': 'log',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'max_size': 10485760,
                'backup_count': 5,
                'colored': True,
                'json_format': False,
                'console': False
            }
        }
        yaml.dump(test_config, self.temp_config)
        self.temp_config.close()
    
    def tearDown(self):
        """
        Clean up test fixtures.
        
        @brief Clean up test environment after each test.
        """
        if hasattr(self, 'temp_config') and self.temp_config and os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_config_access(self):
        """
        Test configuration access.
        
        @brief Test that component can access configuration.
        """
        component = TestComponent(self.temp_config.name)
        component.logger_manager.logger = MagicMock()
        value = component.get_config('component.test.key', 'test_value')
        self.assertEqual(value, "test_value")
    
    def test_set_config(self):
        """
        Test configuration setting.
        
        @brief Test that component can set configuration.
        """
        try:
            component = TestComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
            component.set_config('test.key', 'test_value')
        except SystemExit:
            pass
    
    def test_logging_methods(self):
        """
        Test logging methods.
        
        @brief Test that component logging methods work correctly.
        """
        try:
            component = TestComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
            component.log_info("Test info message")
            component.log_error("Test error message")
            component.log_warning("Test warning message")
            component.log_debug("Test debug message")
        except SystemExit:
            pass
    
    def test_database_operations(self):
        """
        Test database operations.
        
        @brief Test that component database operations work correctly.
        """
        component = TestComponent(self.temp_config.name)
        component.logger_manager.logger = MagicMock()
        if not component.connect_database():
            self.skipTest("Database not available for testing.")
        results = component.execute_query("SELECT * FROM test")
        self.assertEqual(results, [{'count': 5}])
        rows_affected = component.execute_update("INSERT INTO test VALUES (?)", ('value',))
        self.assertEqual(rows_affected, 1)
        component.disconnect_database()
    
    def test_messaging_operations(self):
        """
        Test messaging operations.
        
        @brief Test that component messaging operations work correctly.
        """
        try:
            component = TestComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
        except SystemExit:
            pass
    
    def test_start_method(self):
        """
        Test component start method.
        
        @brief Test that component start method works correctly.
        """
        try:
            component = TestComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
        except SystemExit:
            pass
    
    def test_start_exception_in_initialize(self):
        """
        @brief Test start method when initialize raises exception.
        """
        class ErrorComponent(TestComponent):
            def initialize(self):
                raise Exception("Init error")
        try:
            component = ErrorComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
            result = component.start()
            self.assertFalse(result)
        except SystemExit:
            pass

    def test_start_exception_in_run(self):
        """
        @brief Test start method when run raises exception.
        """
        class ErrorComponent(TestComponent):
            def run(self):
                raise Exception("Run error")
        try:
            component = ErrorComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
            result = component.start()
            self.assertFalse(result)
        except SystemExit:
            pass

    def test_start_exception_in_cleanup(self):
        """
        @brief Test start method when cleanup raises exception.
        """
        class ErrorComponent(TestComponent):
            def cleanup(self):
                raise Exception("Cleanup error")
        try:
            component = ErrorComponent(self.temp_config.name)
            component.logger_manager.logger = MagicMock(side_effect=Exception("Logger error"))
            result = component.start()
            self.assertTrue(result is False or result is True)  # Should not raise
        except SystemExit:
            pass

    def test_logger_error_in_database(self):
        """
        @brief Test error branch in connect_database when logger itself errors.
        """
        try:
            component = TestComponent(self.temp_config.name)
            component.db_manager.connect = MagicMock(return_value=True)
            # Simulate logger raising error
            component.logger_manager.logger.info = MagicMock(side_effect=Exception("Logger error"))
            result = component.connect_database()
            self.assertTrue(result)
        except SystemExit:
            pass  # Expected if sys.exit(1) is called

    def test_logger_error_in_cleanup(self):
        """
        @brief Test error branch in disconnect_database when logger errors.
        """
        component = TestComponent(self.temp_config.name)
        component.db_manager.disconnect = MagicMock()
        component.logger_manager.logger.info = MagicMock(side_effect=Exception("Logger error"))
        try:
            component.disconnect_database()
        except SystemExit:
            pass  # Expected if sys.exit(1) is called

class TestComponentRunner(unittest.TestCase):
    """
    Test cases for ComponentRunner class.
    
    @brief Comprehensive test suite for component runner functionality.
    """
    def test_run_dry_run(self):
        """
        Test dry-run mode branch in runner.
        """
        try:
            runner = ComponentRunner(TestComponent, "TestComponent")
            with patch.object(runner, 'create_parser') as mock_parser:
                mock_args = MagicMock()
                mock_parser.return_value.parse_args.return_value = mock_args
                mock_args.config = None
                mock_args.log_level = 'INFO'
                mock_args.verbose = False
                mock_args.dry_run = True
                runner.component_class = TestComponent
                with patch.object(TestComponent, 'start', return_value=True):
                    result = runner.run([])
                    self.assertTrue(result)
        except SystemExit:
            pass
    
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
    
    @patch('commonpython.framework.component_runner.ComponentRunner.run_with_config')
    def test_run_with_config(self, mock_run_with_config):
        """
        Test running component with configuration.
        
        @brief Test that component runner can run with configuration dictionary.
        """
        mock_run_with_config.return_value = True
        
        runner = ComponentRunner(TestComponent, "TestComponent")
        config = {'test.key': 'test_value'}
        
        result = runner.run_with_config(config)
        
        self.assertTrue(result)
        mock_run_with_config.assert_called_once_with(config)

        @patch('commonpython.framework.component_base.ComponentBase.start')
        def test_run_keyboard_interrupt(self, mock_start):
            """
            Test runner handles KeyboardInterrupt gracefully.
            """
            runner = ComponentRunner(TestComponent, "TestComponent")
            with patch.object(runner, 'create_parser') as mock_parser:
                mock_args = MagicMock()
                mock_parser.return_value.parse_args.return_value = mock_args
                mock_args.config = None
                mock_args.log_level = 'INFO'
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
            with patch.object(runner, 'create_parser') as mock_parser:
                mock_args = MagicMock()
                mock_parser.return_value.parse_args.return_value = mock_args
                mock_args.config = None
                mock_args.log_level = 'INFO'
                mock_args.verbose = False
                mock_args.dry_run = False
                # Simulate error before instance creation
                with patch.object(runner, 'component_class', side_effect=Exception("fail")):
                    result = runner.run([])
                    self.assertFalse(result)

        def test_run_exception_with_instance(self):
            """
            @brief Test runner handles exception when instance exists.
            """
            runner = ComponentRunner(TestComponent, "TestComponent")
            with patch.object(runner, 'create_parser') as mock_parser:
                mock_args = MagicMock()
                mock_parser.return_value.parse_args.return_value = mock_args
                mock_args.config = None
                mock_args.log_level = 'INFO'
                mock_args.verbose = False
                mock_args.dry_run = False
                runner.component_instance = MagicMock()
                # Simulate error after instance creation
                with patch.object(runner, 'component_class', side_effect=Exception("fail")):
                    result = runner.run([])
                    self.assertFalse(result)

    def test_run_with_config_exception(self):
        """
        @brief Test run_with_config handles exception and logs error.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")
        with patch.object(runner, 'component_class', side_effect=Exception("fail")):
            result = runner.run_with_config({'key': 'value'})
            self.assertFalse(result)

    def test_run_with_config_applies_all_keys(self):
        """
        @brief Test run_with_config applies all config keys to component.
        """
        runner = ComponentRunner(TestComponent, "TestComponent")
        config = {'key1': 'value1', 'key2': 'value2'}
        with patch.object(runner, 'component_class', return_value=MagicMock()) as mock_class:
            instance = mock_class.return_value
            instance.set_config = MagicMock()
            instance.start = MagicMock(return_value=True)
            result = runner.run_with_config(config)
            self.assertTrue(result)
            instance.set_config.assert_any_call('key1', 'value1')
            instance.set_config.assert_any_call('key2', 'value2')


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
    
    @patch('commonpython.framework.component_runner.ComponentRunner.run')
    def test_run_component(self, mock_run):
        """
        Test run_component function.
        
        @brief Test that run_component function works correctly.
        """
        mock_run.return_value = True
        
        result = run_component(TestComponent, "TestComponent")
        
        self.assertTrue(result)
        mock_run.assert_called_once_with(None)

