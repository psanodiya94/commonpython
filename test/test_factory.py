"""
Tests for Manager Factory

Comprehensive test suite for ManagerFactory to ensure proper creation
of database and messaging managers based on configuration.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.factories import ManagerFactory
from commonpython.interfaces import IDatabaseManager, IMessagingManager
from commonpython.adapters import DB2CLIAdapter, MQCLIAdapter


class TestManagerFactory(unittest.TestCase):
    """Test suite for ManagerFactory"""

    def setUp(self):
        """Set up test fixtures"""
        self.db_config_cli = {
            'implementation': 'cli',
            'host': 'localhost',
            'port': 50000,
            'name': 'testdb',
            'user': 'testuser',
            'password': 'testpass'
        }

        self.db_config_library = {
            'implementation': 'library',
            'auto_fallback': False,
            'host': 'localhost',
            'port': 50000,
            'name': 'testdb',
            'user': 'testuser',
            'password': 'testpass'
        }

        self.mq_config_cli = {
            'implementation': 'cli',
            'host': 'localhost',
            'port': 1414,
            'queue_manager': 'QM1',
            'channel': 'SYSTEM.DEF.SVRCONN'
        }

        self.mq_config_library = {
            'implementation': 'library',
            'auto_fallback': False,
            'host': 'localhost',
            'port': 1414,
            'queue_manager': 'QM1',
            'channel': 'SYSTEM.DEF.SVRCONN'
        }

        self.logger = Mock()
        self.logger.logger = Mock()

        # Reset factory cache
        ManagerFactory.reset_cache()

    def tearDown(self):
        """Clean up after tests"""
        ManagerFactory.reset_cache()

    def test_create_database_manager_cli(self):
        """Test creating CLI database manager"""
        manager = ManagerFactory.create_database_manager(self.db_config_cli, self.logger)

        self.assertIsInstance(manager, IDatabaseManager)
        self.assertIsInstance(manager, DB2CLIAdapter)

    def test_create_database_manager_default(self):
        """Test creating database manager with default implementation"""
        config = self.db_config_cli.copy()
        del config['implementation']

        manager = ManagerFactory.create_database_manager(config, self.logger)

        self.assertIsInstance(manager, IDatabaseManager)
        self.assertIsInstance(manager, DB2CLIAdapter)

    def test_create_database_manager_invalid_type(self):
        """Test creating database manager with invalid implementation type"""
        config = self.db_config_cli.copy()
        config['implementation'] = 'invalid'

        with self.assertRaises(ValueError) as context:
            ManagerFactory.create_database_manager(config, self.logger)

        self.assertIn('Unknown database implementation', str(context.exception))

    def test_create_database_manager_library_with_fallback(self):
        """Test creating library database manager with auto-fallback"""
        config = self.db_config_library.copy()
        config['auto_fallback'] = True

        # Mock library adapter as unavailable
        ManagerFactory._adapter_cache['db2_library_available'] = False

        manager = ManagerFactory.create_database_manager(config, self.logger)

        # Should fallback to CLI
        self.assertIsInstance(manager, DB2CLIAdapter)
        self.logger.logger.warning.assert_called()

    def test_create_database_manager_library_without_fallback(self):
        """Test creating library database manager without auto-fallback raises error"""
        config = self.db_config_library.copy()
        config['auto_fallback'] = False

        # Mock library adapter as unavailable
        ManagerFactory._adapter_cache['db2_library_available'] = False

        with self.assertRaises(ValueError) as context:
            ManagerFactory.create_database_manager(config, self.logger)

        self.assertIn('ibm_db is not installed', str(context.exception))

    def test_create_messaging_manager_cli(self):
        """Test creating CLI messaging manager"""
        manager = ManagerFactory.create_messaging_manager(self.mq_config_cli, self.logger)

        self.assertIsInstance(manager, IMessagingManager)
        self.assertIsInstance(manager, MQCLIAdapter)

    def test_create_messaging_manager_default(self):
        """Test creating messaging manager with default implementation"""
        config = self.mq_config_cli.copy()
        del config['implementation']

        manager = ManagerFactory.create_messaging_manager(config, self.logger)

        self.assertIsInstance(manager, IMessagingManager)
        self.assertIsInstance(manager, MQCLIAdapter)

    def test_create_messaging_manager_invalid_type(self):
        """Test creating messaging manager with invalid implementation type"""
        config = self.mq_config_cli.copy()
        config['implementation'] = 'invalid'

        with self.assertRaises(ValueError) as context:
            ManagerFactory.create_messaging_manager(config, self.logger)

        self.assertIn('Unknown messaging implementation', str(context.exception))

    def test_create_messaging_manager_library_with_fallback(self):
        """Test creating library messaging manager with auto-fallback"""
        config = self.mq_config_library.copy()
        config['auto_fallback'] = True

        # Mock library adapter as unavailable
        ManagerFactory._adapter_cache['mq_library_available'] = False

        manager = ManagerFactory.create_messaging_manager(config, self.logger)

        # Should fallback to CLI
        self.assertIsInstance(manager, MQCLIAdapter)
        self.logger.logger.warning.assert_called()

    def test_create_messaging_manager_library_without_fallback(self):
        """Test creating library messaging manager without auto-fallback raises error"""
        config = self.mq_config_library.copy()
        config['auto_fallback'] = False

        # Mock library adapter as unavailable
        ManagerFactory._adapter_cache['mq_library_available'] = False

        with self.assertRaises(ValueError) as context:
            ManagerFactory.create_messaging_manager(config, self.logger)

        self.assertIn('pymqi is not installed', str(context.exception))

    def test_get_available_implementations(self):
        """Test getting available implementations"""
        available = ManagerFactory.get_available_implementations()

        self.assertIn('database', available)
        self.assertIn('messaging', available)
        self.assertIn('cli', available['database'])
        self.assertIn('library', available['database'])
        self.assertIn('cli', available['messaging'])
        self.assertIn('library', available['messaging'])

        # CLI should always be available
        self.assertTrue(available['database']['cli'])
        self.assertTrue(available['messaging']['cli'])

    def test_factory_cache(self):
        """Test that factory caches adapter availability"""
        # First call should check availability
        ManagerFactory._adapter_cache['db2_library_available'] = None
        config = self.db_config_cli.copy()

        manager1 = ManagerFactory.create_database_manager(config, self.logger)

        # Cache should be populated
        self.assertIsNotNone(ManagerFactory._adapter_cache['db2_library_available'])

        # Second call should use cache
        manager2 = ManagerFactory.create_database_manager(config, self.logger)

        self.assertIsInstance(manager1, IDatabaseManager)
        self.assertIsInstance(manager2, IDatabaseManager)

    def test_reset_cache(self):
        """Test resetting factory cache"""
        # Populate cache
        ManagerFactory._adapter_cache['db2_library_available'] = True
        ManagerFactory._adapter_cache['mq_library_available'] = True

        # Reset cache
        ManagerFactory.reset_cache()

        # Cache should be cleared
        self.assertIsNone(ManagerFactory._adapter_cache['db2_library_available'])
        self.assertIsNone(ManagerFactory._adapter_cache['mq_library_available'])

    def test_create_without_logger(self):
        """Test creating managers without logger"""
        db_manager = ManagerFactory.create_database_manager(self.db_config_cli, None)
        mq_manager = ManagerFactory.create_messaging_manager(self.mq_config_cli, None)

        self.assertIsInstance(db_manager, IDatabaseManager)
        self.assertIsInstance(mq_manager, IMessagingManager)


class TestManagerFactoryIntegration(unittest.TestCase):
    """Integration tests for ManagerFactory with real adapters"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger = Mock()
        self.logger.logger = Mock()
        ManagerFactory.reset_cache()

    def tearDown(self):
        """Clean up after tests"""
        ManagerFactory.reset_cache()

    def test_cli_to_library_migration(self):
        """Test migration from CLI to library implementation"""
        # Start with CLI
        cli_config = {
            'implementation': 'cli',
            'host': 'localhost',
            'port': 50000,
            'name': 'testdb'
        }

        cli_manager = ManagerFactory.create_database_manager(cli_config, self.logger)
        self.assertIsInstance(cli_manager, DB2CLIAdapter)

        # Switch to library (will fallback to CLI if library not available)
        library_config = {
            'implementation': 'library',
            'auto_fallback': True,
            'host': 'localhost',
            'port': 50000,
            'name': 'testdb'
        }

        library_manager = ManagerFactory.create_database_manager(library_config, self.logger)
        self.assertIsInstance(library_manager, IDatabaseManager)

        # Both should implement the same interface
        self.assertIsInstance(cli_manager, IDatabaseManager)
        self.assertIsInstance(library_manager, IDatabaseManager)

    def test_parallel_implementations(self):
        """Test using both implementations simultaneously"""
        cli_config = {'implementation': 'cli', 'host': 'localhost', 'port': 50000, 'name': 'testdb'}
        library_config = {'implementation': 'library', 'auto_fallback': True, 'host': 'localhost', 'port': 50000, 'name': 'testdb'}

        cli_manager = ManagerFactory.create_database_manager(cli_config, self.logger)
        library_manager = ManagerFactory.create_database_manager(library_config, self.logger)

        # Both should be valid manager instances
        self.assertIsInstance(cli_manager, IDatabaseManager)
        self.assertIsInstance(library_manager, IDatabaseManager)

        # They should be different instances
        self.assertIsNot(cli_manager, library_manager)


if __name__ == '__main__':
    unittest.main()
