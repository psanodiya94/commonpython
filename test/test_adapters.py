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


if __name__ == "__main__":
    unittest.main()
