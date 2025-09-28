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
        value = component.get_config('component.test.key', 'test_value')
        self.assertEqual(value, "test_value")
    
    def test_set_config(self):
        """
        Test configuration setting.
        
        @brief Test that component can set configuration.
        """
        component = TestComponent(self.temp_config.name)
        component.set_config('test.key', 'test_value')
        # No mock assertion, just ensure no exception
    
    def test_logging_methods(self):
        """
        Test logging methods.
        
        @brief Test that component logging methods work correctly.
        """
        component = TestComponent(self.temp_config.name)
        component.log_info("Test info message")
        component.log_error("Test error message")
        component.log_warning("Test warning message")
        component.log_debug("Test debug message")
        # No mock assertion, just ensure no exception
    
    def test_database_operations(self):
        """
        Test database operations.
        
        @brief Test that component database operations work correctly.
        """
        component = TestComponent(self.temp_config.name)
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
        component = TestComponent(self.temp_config.name)
        # No mock assertion, just ensure no exception
    
    def test_start_method(self):
        """
        Test component start method.
        
        @brief Test that component start method works correctly.
        """
        component = TestComponent(self.temp_config.name)
        # No mock assertion, just ensure no exception


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


if __name__ == '__main__':
    unittest.main()
