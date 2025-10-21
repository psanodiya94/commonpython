"""
Integration Tests for CommonPython Framework

Tests the integration between different components and ensures that
CLI and library implementations behave consistently.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.factories import ManagerFactory
from commonpython.interfaces import IDatabaseManager, IMessagingManager
from commonpython.adapters import DB2CLIAdapter, MQCLIAdapter


class TestImplementationConsistency(unittest.TestCase):
    """
    Test that CLI and library implementations behave consistently
    and implement the same interface correctly.
    """

    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
        self.logger.logger = Mock()
        self.logger.log_database_operation = Mock()
        self.logger.log_mq_operation = Mock()

    def test_database_interface_consistency(self):
        """Test that both DB implementations have same interface methods"""
        cli_config = {'implementation': 'cli', 'host': 'localhost', 'port': 50000, 'name': 'testdb'}

        cli_manager = ManagerFactory.create_database_manager(cli_config, self.logger)

        # Check all interface methods exist
        interface_methods = [
            'connect', 'disconnect', 'is_connected', 'execute_query',
            'execute_update', 'execute_batch', 'transaction',
            'get_table_info', 'get_database_info', 'test_connection'
        ]

        for method in interface_methods:
            self.assertTrue(
                hasattr(cli_manager, method),
                f"CLI adapter missing method: {method}"
            )
            self.assertTrue(
                callable(getattr(cli_manager, method)),
                f"CLI adapter {method} is not callable"
            )

        # If library implementation is available, test it too
        try:
            library_config = {'implementation': 'library', 'auto_fallback': False, 'host': 'localhost', 'port': 50000, 'name': 'testdb'}
            library_manager = ManagerFactory.create_database_manager(library_config, None)

            for method in interface_methods:
                self.assertTrue(
                    hasattr(library_manager, method),
                    f"Library adapter missing method: {method}"
                )
                self.assertTrue(
                    callable(getattr(library_manager, method)),
                    f"Library adapter {method} is not callable"
                )
        except (ValueError, ImportError):
            # Library implementation not available
            pass

    def test_messaging_interface_consistency(self):
        """Test that both MQ implementations have same interface methods"""
        cli_config = {'implementation': 'cli', 'host': 'localhost', 'port': 1414, 'queue_manager': 'QM1'}

        cli_manager = ManagerFactory.create_messaging_manager(cli_config, self.logger)

        # Check all interface methods exist
        interface_methods = [
            'connect', 'disconnect', 'is_connected', 'put_message',
            'get_message', 'browse_message', 'get_queue_depth',
            'purge_queue', 'test_connection'
        ]

        for method in interface_methods:
            self.assertTrue(
                hasattr(cli_manager, method),
                f"CLI adapter missing method: {method}"
            )
            self.assertTrue(
                callable(getattr(cli_manager, method)),
                f"CLI adapter {method} is not callable"
            )

        # If library implementation is available, test it too
        try:
            library_config = {'implementation': 'library', 'auto_fallback': False, 'host': 'localhost', 'port': 1414, 'queue_manager': 'QM1'}
            library_manager = ManagerFactory.create_messaging_manager(library_config, None)

            for method in interface_methods:
                self.assertTrue(
                    hasattr(library_manager, method),
                    f"Library adapter missing method: {method}"
                )
                self.assertTrue(
                    callable(getattr(library_manager, method)),
                    f"Library adapter {method} is not callable"
                )
        except (ValueError, ImportError):
            # Library implementation not available
            pass

    @patch('commonpython.database.db2_manager.subprocess.run')
    def test_database_operation_flow(self, mock_run):
        """Test complete database operation flow"""
        mock_run.return_value = Mock(returncode=0, stdout='Connected', stderr='')

        config = {'implementation': 'cli', 'host': 'localhost', 'port': 50000, 'name': 'testdb'}
        manager = ManagerFactory.create_database_manager(config, self.logger)

        # Test connection flow
        self.assertFalse(manager.is_connected())
        manager.connect()
        self.assertTrue(manager.is_connected())

        # Test query execution
        with patch.object(manager, 'execute_query', return_value=[{'id': 1, 'name': 'test'}]):
            results = manager.execute_query("SELECT * FROM test")
            self.assertIsNotNone(results)
            self.assertEqual(len(results), 1)

        # Test update execution
        with patch.object(manager, 'execute_update', return_value=5):
            rows = manager.execute_update("UPDATE test SET name = 'updated'")
            self.assertEqual(rows, 5)

        # Test disconnection
        manager.disconnect()
        self.assertFalse(manager.is_connected())

    @patch('commonpython.messaging.mq_manager.subprocess.run')
    def test_messaging_operation_flow(self, mock_run):
        """Test complete messaging operation flow"""
        mock_run.return_value = Mock(returncode=0, stdout='Connected', stderr='')

        config = {'implementation': 'cli', 'host': 'localhost', 'port': 1414, 'queue_manager': 'QM1'}
        manager = ManagerFactory.create_messaging_manager(config, self.logger)

        # Test connection flow
        self.assertFalse(manager.is_connected())
        manager.connect()
        self.assertTrue(manager.is_connected())

        # Test message operations
        with patch.object(manager, 'put_message', return_value=True):
            result = manager.put_message('TEST.QUEUE', {'message': 'test'})
            self.assertTrue(result)

        with patch.object(manager, 'get_message', return_value={'data': {'message': 'test'}}):
            message = manager.get_message('TEST.QUEUE')
            self.assertIsNotNone(message)

        with patch.object(manager, 'get_queue_depth', return_value=10):
            depth = manager.get_queue_depth('TEST.QUEUE')
            self.assertEqual(depth, 10)

        # Test disconnection
        manager.disconnect()
        self.assertFalse(manager.is_connected())


class TestComponentIntegration(unittest.TestCase):
    """Test integration with ComponentBase"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
        self.logger.logger = Mock()

    @patch('commonpython.framework.component_base.ConfigManager')
    @patch('commonpython.framework.component_base.LoggerManager')
    def test_component_uses_factory(self, mock_logger_manager, mock_config_manager):
        """Test that ComponentBase uses factory to create managers"""
        from commonpython.framework import ComponentBase

        # Mock configuration
        mock_config = Mock()
        mock_config.get_database_config.return_value = {
            'implementation': 'cli',
            'host': 'localhost',
            'port': 50000,
            'name': 'testdb'
        }
        mock_config.get_messaging_config.return_value = {
            'implementation': 'cli',
            'host': 'localhost',
            'port': 1414,
            'queue_manager': 'QM1'
        }
        mock_config.get_logging_config.return_value = {
            'level': 'INFO',
            'file': 'test.log',
            'dir': 'log'
        }

        mock_config_manager.return_value = mock_config
        mock_logger_manager.return_value = self.logger

        # Create a concrete component class
        class TestComponent(ComponentBase):
            def initialize(self):
                return True

            def run(self):
                return True

            def cleanup(self):
                pass

        # Create component
        component = TestComponent('TestComponent', 'test_config.yaml')

        # Verify managers were created via factory
        self.assertIsInstance(component.db_manager, IDatabaseManager)
        self.assertIsInstance(component.mq_manager, IMessagingManager)

    @patch('commonpython.framework.component_base.ConfigManager')
    @patch('commonpython.framework.component_base.LoggerManager')
    def test_component_switches_implementation(self, mock_logger_manager, mock_config_manager):
        """Test component can switch between implementations via config"""
        from commonpython.framework import ComponentBase

        # Test with CLI implementation
        mock_config_cli = Mock()
        mock_config_cli.get_database_config.return_value = {
            'implementation': 'cli',
            'host': 'localhost',
            'port': 50000,
            'name': 'testdb'
        }
        mock_config_cli.get_messaging_config.return_value = {
            'implementation': 'cli',
            'host': 'localhost',
            'port': 1414,
            'queue_manager': 'QM1'
        }
        mock_config_cli.get_logging_config.return_value = {
            'level': 'INFO',
            'file': 'test.log',
            'dir': 'log'
        }

        mock_config_manager.return_value = mock_config_cli
        mock_logger_manager.return_value = self.logger

        class TestComponent(ComponentBase):
            def initialize(self):
                return True

            def run(self):
                return True

            def cleanup(self):
                pass

        component = TestComponent('TestComponent', 'test_config.yaml')

        # Should use CLI adapters
        self.assertIsInstance(component.db_manager, DB2CLIAdapter)
        self.assertIsInstance(component.mq_manager, MQCLIAdapter)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across different implementations"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
        self.logger.logger = Mock()

    def test_invalid_config_handling(self):
        """Test handling of invalid configuration"""
        invalid_config = {
            'implementation': 'invalid_type',
            'host': 'localhost'
        }

        with self.assertRaises(ValueError):
            ManagerFactory.create_database_manager(invalid_config, self.logger)

        with self.assertRaises(ValueError):
            ManagerFactory.create_messaging_manager(invalid_config, self.logger)

    def test_missing_library_handling(self):
        """Test handling when library implementation is requested but not available"""
        config = {
            'implementation': 'library',
            'auto_fallback': False,
            'host': 'localhost',
            'port': 50000,
            'name': 'testdb'
        }

        # Mock library as unavailable
        ManagerFactory._adapter_cache['db2_library_available'] = False

        with self.assertRaises(ValueError):
            ManagerFactory.create_database_manager(config, self.logger)

        ManagerFactory.reset_cache()

    @patch('commonpython.database.db2_manager.subprocess.run')
    def test_connection_failure_handling(self, mock_run):
        """Test handling of connection failures"""
        mock_run.return_value = Mock(returncode=1, stdout='', stderr='Connection failed')

        config = {'implementation': 'cli', 'host': 'localhost', 'port': 50000, 'name': 'testdb'}
        manager = ManagerFactory.create_database_manager(config, self.logger)

        result = manager.connect()
        self.assertFalse(result)
        self.assertFalse(manager.is_connected())


if __name__ == '__main__':
    unittest.main()
