"""
Tests for Database and Messaging Adapters

Comprehensive test suite for CLI and library-based adapters to ensure
they properly implement the interface contracts and work correctly.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.adapters import DB2CLIAdapter, MQCLIAdapter  # noqa: E402
from commonpython.interfaces import IDatabaseManager, IMessagingManager  # noqa: E402


class TestDB2CLIAdapter(unittest.TestCase):
    """Test suite for DB2 CLI adapter"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "host": "localhost",
            "port": 50000,
            "database": "testdb",
            "name": "testdb",
            "user": "testuser",
            "password": "testpass",
            "schema": "testschema",
            "timeout": 30,
        }
        self.logger = Mock()
        self.logger.logger = Mock()

    def test_adapter_implements_interface(self):
        """Test that adapter properly implements IDatabaseManager interface"""
        adapter = DB2CLIAdapter(self.config, self.logger)
        self.assertIsInstance(adapter, IDatabaseManager)

    def test_adapter_initialization(self):
        """Test adapter initialization"""
        adapter = DB2CLIAdapter(self.config, self.logger)
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter._config, self.config)
        self.assertEqual(adapter._logger, self.logger)

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_connect(self, mock_run):
        """Test database connection"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        result = adapter.connect()

        self.assertTrue(result)
        self.assertTrue(adapter.is_connected())

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_connect_failure(self, mock_run):
        """Test database connection failure"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Connection failed")

        adapter = DB2CLIAdapter(self.config, self.logger)
        result = adapter.connect()

        self.assertFalse(result)
        self.assertFalse(adapter.is_connected())

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_disconnect(self, mock_run):
        """Test database disconnection"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        adapter.connect()
        adapter.disconnect()

        self.assertFalse(adapter.is_connected())

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_execute_query(self, mock_run):
        """Test query execution"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock the query execution
        with patch.object(adapter._impl, "execute_query", return_value=[{"id": 1, "name": "test"}]):
            results = adapter.execute_query("SELECT * FROM test")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["id"], 1)

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_execute_update(self, mock_run):
        """Test update execution"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock the update execution
        with patch.object(adapter._impl, "execute_update", return_value=5):
            rows_affected = adapter.execute_update("UPDATE test SET name = 'updated'")
            self.assertEqual(rows_affected, 5)

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_transaction_context_manager(self, mock_run):
        """Test transaction context manager"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock transaction methods
        with patch.object(adapter._impl, "transaction"):
            with adapter.transaction():
                pass  # Transaction should commit successfully

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_execute_batch(self, mock_run):
        """Test batch query execution"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock batch execution
        queries = ["UPDATE test SET name='a'", "UPDATE test SET name='b'"]
        params_list = [(), ()]
        with patch.object(adapter._impl, "execute_batch", return_value=[1, 2]):
            results = adapter.execute_batch(queries, params_list)
            self.assertEqual(results, [1, 2])
            self.assertEqual(len(results), 2)

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_get_table_info(self, mock_run):
        """Test getting table information"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock table info retrieval
        expected_info = [{"name": "id", "type": "INTEGER"}, {"name": "name", "type": "VARCHAR"}]
        with patch.object(adapter._impl, "get_table_info", return_value=expected_info):
            table_info = adapter.get_table_info("test_table")
            self.assertEqual(len(table_info), 2)
            self.assertEqual(table_info[0]["name"], "id")

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_get_database_info(self, mock_run):
        """Test getting database information"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock database info retrieval
        expected_info = {"name": "testdb", "version": "11.5"}
        with patch.object(adapter._impl, "get_database_info", return_value=expected_info):
            db_info = adapter.get_database_info()
            self.assertEqual(db_info["name"], "testdb")
            self.assertEqual(db_info["version"], "11.5")

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_connection_test(self, mock_run):
        """Test connection testing method"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = DB2CLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock connection test
        with patch.object(adapter._impl, "test_connection", return_value=True):
            result = adapter.test_connection()
            self.assertTrue(result)


class TestMQCLIAdapter(unittest.TestCase):
    """Test suite for MQ CLI adapter"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "host": "localhost",
            "port": 1414,
            "queue_manager": "QM1",
            "channel": "SYSTEM.DEF.SVRCONN",
            "user": "testuser",
            "password": "testpass",
            "timeout": 30,
        }
        self.logger = Mock()
        self.logger.logger = Mock()

    def test_adapter_implements_interface(self):
        """Test that adapter properly implements IMessagingManager interface"""
        adapter = MQCLIAdapter(self.config, self.logger)
        self.assertIsInstance(adapter, IMessagingManager)

    def test_adapter_initialization(self):
        """Test adapter initialization"""
        adapter = MQCLIAdapter(self.config, self.logger)
        self.assertIsNotNone(adapter)
        self.assertEqual(adapter._config, self.config)
        self.assertEqual(adapter._logger, self.logger)

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_connect(self, mock_run):
        """Test messaging connection"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = MQCLIAdapter(self.config, self.logger)
        result = adapter.connect()

        self.assertTrue(result)
        self.assertTrue(adapter.is_connected())

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_connect_failure(self, mock_run):
        """Test messaging connection failure"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Connection failed")

        adapter = MQCLIAdapter(self.config, self.logger)
        result = adapter.connect()

        self.assertFalse(result)
        self.assertFalse(adapter.is_connected())

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_put_message(self, mock_run):
        """Test message sending"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = MQCLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock the put_message
        with patch.object(adapter._impl, "put_message", return_value=True):
            result = adapter.put_message("TEST.QUEUE", {"message": "test"})
            self.assertTrue(result)

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_get_message(self, mock_run):
        """Test message receiving"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = MQCLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock the get_message
        expected_message = {
            "data": {"message": "test"},
            "properties": {"message_id": "12345"},
            "raw_bytes": b"test",
        }
        with patch.object(adapter._impl, "get_message", return_value=expected_message):
            message = adapter.get_message("TEST.QUEUE")
            self.assertIsNotNone(message)
            self.assertEqual(message["data"]["message"], "test")

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_get_queue_depth(self, mock_run):
        """Test queue depth retrieval"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = MQCLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock the get_queue_depth
        with patch.object(adapter._impl, "get_queue_depth", return_value=10):
            depth = adapter.get_queue_depth("TEST.QUEUE")
            self.assertEqual(depth, 10)

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_browse_message(self, mock_run):
        """Test message browsing without removal"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = MQCLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock the browse_message
        expected_message = {
            "data": {"message": "browse_test"},
            "properties": {"message_id": "67890"},
            "raw_bytes": b"browse_test",
        }
        with patch.object(adapter._impl, "browse_message", return_value=expected_message):
            message = adapter.browse_message("TEST.QUEUE")
            self.assertIsNotNone(message)
            self.assertEqual(message["data"]["message"], "browse_test")

        # Test with message_id
        with patch.object(adapter._impl, "browse_message", return_value=expected_message):
            message = adapter.browse_message("TEST.QUEUE", b"message_id_123")
            self.assertIsNotNone(message)

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_purge_queue(self, mock_run):
        """Test queue purging"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = MQCLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock the purge_queue
        with patch.object(adapter._impl, "purge_queue", return_value=15):
            purged_count = adapter.purge_queue("TEST.QUEUE")
            self.assertEqual(purged_count, 15)

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_connection_test(self, mock_run):
        """Test connection testing method"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        adapter = MQCLIAdapter(self.config, self.logger)
        adapter.connect()

        # Mock connection test
        with patch.object(adapter._impl, "test_connection", return_value=True):
            result = adapter.test_connection()
            self.assertTrue(result)


class TestLibraryAdapters(unittest.TestCase):
    """Test suite for library-based adapters (when available)"""

    def test_db2_library_adapter_import(self):
        """Test importing DB2 library adapter"""
        try:
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            self.assertTrue(hasattr(DB2LibraryAdapter, "__init__"))
        except ImportError:
            self.skipTest("ibm_db library not installed")

    def test_mq_library_adapter_import(self):
        """Test importing MQ library adapter"""
        try:
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            self.assertTrue(hasattr(MQLibraryAdapter, "__init__"))
        except ImportError:
            self.skipTest("pymqi library not installed")

    def test_db2_library_adapter_without_library(self):
        """Test DB2 library adapter raises error when ibm_db not installed"""
        with patch.dict("sys.modules", {"ibm_db": None, "ibm_db_dbi": None}):
            try:
                from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

                config = {"host": "localhost", "port": 50000, "name": "testdb"}
                with self.assertRaises(ImportError):
                    DB2LibraryAdapter(config)
            except ImportError:
                # If module itself can't be imported, that's also acceptable
                pass

    def test_mq_library_adapter_without_library(self):
        """Test MQ library adapter raises error when pymqi not installed"""
        with patch.dict("sys.modules", {"pymqi": None}):
            try:
                from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

                config = {"host": "localhost", "port": 1414, "queue_manager": "QM1"}
                with self.assertRaises(ImportError):
                    MQLibraryAdapter(config)
            except ImportError:
                # If module itself can't be imported, that's also acceptable
                pass


class TestAdapterInitModule(unittest.TestCase):
    """Test suite for adapters/__init__.py module"""

    def test_adapters_module_has_base_exports(self):
        """Test that adapters module exports CLI adapters"""
        from commonpython import adapters

        self.assertTrue(hasattr(adapters, "DB2CLIAdapter"))
        self.assertTrue(hasattr(adapters, "MQCLIAdapter"))
        self.assertIn("DB2CLIAdapter", adapters.__all__)
        self.assertIn("MQCLIAdapter", adapters.__all__)

    def test_adapters_module_library_flags(self):
        """Test that adapters module has library availability flags"""
        from commonpython import adapters

        self.assertTrue(hasattr(adapters, "HAS_DB2_LIBRARY"))
        self.assertTrue(hasattr(adapters, "HAS_MQ_LIBRARY"))
        self.assertIsInstance(adapters.HAS_DB2_LIBRARY, bool)
        self.assertIsInstance(adapters.HAS_MQ_LIBRARY, bool)

    def test_adapters_module_conditional_exports(self):
        """Test that library adapters are conditionally added to __all__"""
        from commonpython import adapters

        # If libraries are available, they should be in __all__
        if adapters.HAS_DB2_LIBRARY:
            self.assertIn("DB2LibraryAdapter", adapters.__all__)
            self.assertTrue(hasattr(adapters, "DB2LibraryAdapter"))
        else:
            # If not available, should not be in __all__
            if "DB2LibraryAdapter" in adapters.__all__:
                self.fail("DB2LibraryAdapter in __all__ but HAS_DB2_LIBRARY is False")

        if adapters.HAS_MQ_LIBRARY:
            self.assertIn("MQLibraryAdapter", adapters.__all__)
            self.assertTrue(hasattr(adapters, "MQLibraryAdapter"))
        else:
            # If not available, should not be in __all__
            if "MQLibraryAdapter" in adapters.__all__:
                self.fail("MQLibraryAdapter in __all__ but HAS_MQ_LIBRARY is False")

    def test_import_error_handling_db2(self):
        """Test DB2 library import error handling"""
        import builtins
        import importlib
        import sys

        # Save original modules
        original_modules = sys.modules.copy()
        original_import = builtins.__import__

        try:
            # Remove adapters module from sys.modules to force reimport
            for mod in list(sys.modules.keys()):
                if mod.startswith("commonpython.adapters"):
                    del sys.modules[mod]

            # Create a mock module that raises ImportError for db2_library_adapter
            def mock_import(name, *args, **kwargs):
                if "db2_library_adapter" in name:
                    raise ImportError(f"No module named '{name}'")
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                # This import should hit the ImportError path on lines 16-17
                import commonpython.adapters as test_adapters

                # Verify DB2 library is marked as unavailable
                self.assertFalse(test_adapters.HAS_DB2_LIBRARY)
                self.assertNotIn("DB2LibraryAdapter", test_adapters.__all__)

        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_import_error_handling_mq(self):
        """Test MQ library import error handling"""
        import builtins
        import importlib
        import sys

        # Save original modules
        original_modules = sys.modules.copy()
        original_import = builtins.__import__

        try:
            # Remove adapters module from sys.modules to force reimport
            for mod in list(sys.modules.keys()):
                if mod.startswith("commonpython.adapters"):
                    del sys.modules[mod]

            # Create a mock module that raises ImportError for mq_library_adapter
            def mock_import(name, *args, **kwargs):
                if "mq_library_adapter" in name:
                    raise ImportError(f"No module named '{name}'")
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                # This import should hit the ImportError path on lines 23-24
                import commonpython.adapters as test_adapters

                # Verify MQ library is marked as unavailable
                self.assertFalse(test_adapters.HAS_MQ_LIBRARY)
                self.assertNotIn("MQLibraryAdapter", test_adapters.__all__)

        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)


if __name__ == "__main__":
    unittest.main()
