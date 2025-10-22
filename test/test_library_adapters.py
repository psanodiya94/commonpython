"""
Comprehensive Tests for Library-Based Adapters

Test suite for DB2LibraryAdapter and MQLibraryAdapter with mocked
library dependencies to ensure comprehensive code coverage.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call, PropertyMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDB2LibraryAdapter(unittest.TestCase):
    """Comprehensive test suite for DB2LibraryAdapter"""

    def setUp(self):
        """Set up test fixtures with mocked ibm_db"""
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

        # Mock ibm_db and ibm_db_dbi modules
        self.mock_ibm_db = MagicMock()
        self.mock_ibm_db_dbi = MagicMock()

        # Setup module patches
        self.ibm_db_patcher = patch.dict('sys.modules', {
            'ibm_db': self.mock_ibm_db,
            'ibm_db_dbi': self.mock_ibm_db_dbi
        })
        self.ibm_db_patcher.start()

    def tearDown(self):
        """Clean up patches"""
        self.ibm_db_patcher.stop()
        # Clear the module from cache if it was imported
        if 'commonpython.adapters.db2_library_adapter' in sys.modules:
            del sys.modules['commonpython.adapters.db2_library_adapter']

    def test_initialization_with_library(self):
        """Test adapter initialization when ibm_db is available"""
        # Mock HAS_IBM_DB = True
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            adapter = DB2LibraryAdapter(self.config, self.logger)
            self.assertIsNotNone(adapter)
            self.assertEqual(adapter._config, self.config)
            self.assertEqual(adapter._logger, self.logger)

    def test_initialization_without_library(self):
        """Test adapter initialization raises ImportError when ibm_db not available"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', False):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            with self.assertRaises(ImportError) as context:
                DB2LibraryAdapter(self.config, self.logger)
            self.assertIn("ibm_db library is not installed", str(context.exception))

    def test_initialization_creates_connection_string(self):
        """Test that initialization creates connection string"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            adapter = DB2LibraryAdapter(self.config, self.logger)
            # Connection string should be created during initialization
            self.assertIsNotNone(adapter._connection_string)
            self.assertIsInstance(adapter._connection_string, str)

    def test_connect_success(self):
        """Test successful database connection"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            # Mock successful connection
            mock_conn = Mock()
            mock_dbi_conn = Mock()
            self.mock_ibm_db.connect.return_value = mock_conn
            self.mock_ibm_db_dbi.Connection.return_value = mock_dbi_conn

            adapter = DB2LibraryAdapter(self.config, self.logger)
            result = adapter.connect()

            self.assertTrue(result)
            self.assertEqual(adapter._conn, mock_conn)
            self.assertEqual(adapter._dbi_conn, mock_dbi_conn)
            self.logger.logger.info.assert_called()

    def test_connect_failure(self):
        """Test database connection failure"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            # Mock connection failure
            self.mock_ibm_db.connect.side_effect = Exception("Connection failed")

            adapter = DB2LibraryAdapter(self.config, self.logger)
            result = adapter.connect()

            self.assertFalse(result)
            self.logger.logger.error.assert_called()

    def test_connect_without_logger(self):
        """Test connection without logger"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_conn = Mock()
            mock_dbi_conn = Mock()
            self.mock_ibm_db.connect.return_value = mock_conn
            self.mock_ibm_db_dbi.Connection.return_value = mock_dbi_conn

            adapter = DB2LibraryAdapter(self.config, None)
            result = adapter.connect()

            self.assertTrue(result)

    def test_disconnect_success(self):
        """Test successful disconnection"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_conn = Mock()
            mock_dbi_conn = Mock()

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = mock_conn
            adapter._dbi_conn = mock_dbi_conn

            adapter.disconnect()

            mock_dbi_conn.close.assert_called_once()
            self.mock_ibm_db.close.assert_called_once_with(mock_conn)
            self.assertIsNone(adapter._conn)
            self.assertIsNone(adapter._dbi_conn)

    def test_disconnect_with_error(self):
        """Test disconnection with error"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_conn = Mock()
            mock_dbi_conn = Mock()
            mock_dbi_conn.close.side_effect = Exception("Close failed")

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = mock_conn
            adapter._dbi_conn = mock_dbi_conn

            adapter.disconnect()

            self.logger.logger.error.assert_called()

    def test_is_connected_true(self):
        """Test is_connected returns True when connected"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_conn = Mock()
            self.mock_ibm_db.active.return_value = True

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = mock_conn

            self.assertTrue(adapter.is_connected())

    def test_is_connected_false(self):
        """Test is_connected returns False when not connected"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = None

            self.assertFalse(adapter.is_connected())

    def test_is_connected_exception(self):
        """Test is_connected handles exceptions"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_conn = Mock()
            self.mock_ibm_db.active.side_effect = Exception("Check failed")

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = mock_conn

            self.assertFalse(adapter.is_connected())

    def test_execute_query_success(self):
        """Test successful query execution"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            # Setup mocks
            mock_cursor = Mock()
            mock_cursor.description = [("ID",), ("NAME",)]
            mock_cursor.fetchall.return_value = [(1, "test"), (2, "test2")]

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            results = adapter.execute_query("SELECT * FROM test")

            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]["ID"], 1)
            self.assertEqual(results[0]["NAME"], "test")
            mock_cursor.execute.assert_called_once()
            mock_cursor.close.assert_called_once()

    def test_execute_query_with_params(self):
        """Test query execution with parameters"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.description = [("ID",)]
            mock_cursor.fetchall.return_value = [(1,)]

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            results = adapter.execute_query("SELECT * FROM test WHERE id = ?", (1,))

            self.assertEqual(len(results), 1)
            mock_cursor.execute.assert_called_once_with("SELECT * FROM test WHERE id = ?", (1,))

    def test_execute_query_not_connected(self):
        """Test query execution when not connected"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            adapter = DB2LibraryAdapter(self.config, self.logger)

            with self.assertRaises(Exception) as context:
                adapter.execute_query("SELECT * FROM test")
            self.assertIn("Database connection not established", str(context.exception))

    def test_execute_query_error(self):
        """Test query execution with error"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.execute.side_effect = Exception("Query failed")

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            with self.assertRaises(Exception):
                adapter.execute_query("SELECT * FROM test")

            self.logger.logger.error.assert_called()

    def test_execute_update_success(self):
        """Test successful update execution"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.rowcount = 5

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            rows = adapter.execute_update("UPDATE test SET name = 'updated'")

            self.assertEqual(rows, 5)
            mock_cursor.execute.assert_called_once()
            mock_cursor.close.assert_called_once()
            mock_dbi_conn.commit.assert_called_once()

    def test_execute_update_with_params(self):
        """Test update execution with parameters"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.rowcount = 1

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            rows = adapter.execute_update("UPDATE test SET name = ? WHERE id = ?", ("new", 1))

            self.assertEqual(rows, 1)

    def test_execute_update_not_connected(self):
        """Test update execution when not connected"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            adapter = DB2LibraryAdapter(self.config, self.logger)

            with self.assertRaises(Exception) as context:
                adapter.execute_update("UPDATE test SET name = 'updated'")
            self.assertIn("Database connection not established", str(context.exception))

    def test_execute_update_error(self):
        """Test update execution with error"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.execute.side_effect = Exception("Update failed")

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            with self.assertRaises(Exception):
                adapter.execute_update("UPDATE test SET name = 'updated'")

    def test_execute_batch_success(self):
        """Test successful batch execution"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.rowcount = 1

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            queries = ["INSERT INTO test VALUES (?)", "INSERT INTO test VALUES (?)"]
            params = [(1,), (2,)]

            results = adapter.execute_batch(queries, params)

            self.assertEqual(len(results), 2)
            self.assertEqual(mock_cursor.execute.call_count, 2)
            mock_dbi_conn.commit.assert_called_once()

    def test_execute_batch_without_params(self):
        """Test batch execution without parameters"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.rowcount = 1

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            queries = ["INSERT INTO test VALUES (1)", "INSERT INTO test VALUES (2)"]

            results = adapter.execute_batch(queries)

            self.assertEqual(len(results), 2)

    def test_execute_batch_error_rollback(self):
        """Test batch execution error triggers rollback"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.execute.side_effect = Exception("Batch failed")

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            queries = ["INSERT INTO test VALUES (1)"]

            with self.assertRaises(Exception):
                adapter.execute_batch(queries)

            mock_dbi_conn.rollback.assert_called_once()

    def test_transaction_context_success(self):
        """Test successful transaction context"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_dbi_conn = Mock()

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            with adapter.transaction():
                pass

            mock_dbi_conn.commit.assert_called_once()

    def test_transaction_context_error_rollback(self):
        """Test transaction context error triggers rollback"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_dbi_conn = Mock()

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            with self.assertRaises(Exception):
                with adapter.transaction():
                    raise Exception("Transaction error")

            mock_dbi_conn.rollback.assert_called_once()

    def test_transaction_not_connected(self):
        """Test transaction when not connected"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            adapter = DB2LibraryAdapter(self.config, self.logger)

            with self.assertRaises(Exception) as context:
                with adapter.transaction():
                    pass
            self.assertIn("Database connection not established", str(context.exception))

    def test_get_table_info(self):
        """Test getting table information"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.description = [("COLNAME",), ("TYPENAME",), ("LENGTH",), ("SCALE",), ("NULLS",), ("KEYSEQ",)]
            mock_cursor.fetchall.return_value = [("ID", "INTEGER", 4, 0, "N", 1)]

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            info = adapter.get_table_info("test_table")

            self.assertEqual(len(info), 1)
            self.assertEqual(info[0]["COLNAME"], "ID")

    def test_get_database_info(self):
        """Test getting database information"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.description = [("VERSION",)]
            mock_cursor.fetchall.return_value = [("11.5",)]

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            info = adapter.get_database_info()

            self.assertIsInstance(info, dict)

    def test_get_database_info_empty(self):
        """Test getting database information when no results"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.description = [("VERSION",)]
            mock_cursor.fetchall.return_value = []

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            info = adapter.get_database_info()

            self.assertEqual(info, {})

    def test_test_connection_success(self):
        """Test connection test success"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.description = [("1",)]
            mock_cursor.fetchall.return_value = [(1,)]

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            result = adapter.test_connection()

            self.assertTrue(result)

    def test_test_connection_failure(self):
        """Test connection test failure"""
        with patch('commonpython.adapters.db2_library_adapter.HAS_IBM_DB', True):
            from commonpython.adapters.db2_library_adapter import DB2LibraryAdapter

            mock_cursor = Mock()
            mock_cursor.execute.side_effect = Exception("Test failed")

            mock_dbi_conn = Mock()
            mock_dbi_conn.cursor.return_value = mock_cursor

            adapter = DB2LibraryAdapter(self.config, self.logger)
            adapter._conn = Mock()
            adapter._dbi_conn = mock_dbi_conn
            self.mock_ibm_db.active.return_value = True

            result = adapter.test_connection()

            self.assertFalse(result)


class TestMQLibraryAdapter(unittest.TestCase):
    """Comprehensive test suite for MQLibraryAdapter"""

    def setUp(self):
        """Set up test fixtures with mocked pymqi"""
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

        # Mock pymqi module
        self.mock_pymqi = MagicMock()

        # Setup module patches
        self.pymqi_patcher = patch.dict('sys.modules', {
            'pymqi': self.mock_pymqi
        })
        self.pymqi_patcher.start()

    def tearDown(self):
        """Clean up patches"""
        self.pymqi_patcher.stop()
        # Clear the module from cache if it was imported
        if 'commonpython.adapters.mq_library_adapter' in sys.modules:
            del sys.modules['commonpython.adapters.mq_library_adapter']

    def test_initialization_with_library(self):
        """Test adapter initialization when pymqi is available"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            adapter = MQLibraryAdapter(self.config, self.logger)
            self.assertIsNotNone(adapter)
            self.assertEqual(adapter._config, self.config)
            self.assertEqual(adapter._logger, self.logger)

    def test_initialization_without_library(self):
        """Test adapter initialization raises ImportError when pymqi not available"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', False):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            with self.assertRaises(ImportError) as context:
                MQLibraryAdapter(self.config, self.logger)
            self.assertIn("pymqi library is not installed", str(context.exception))

    def test_build_connection_info(self):
        """Test connection info building"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            adapter = MQLibraryAdapter(self.config, self.logger)
            conn_info = adapter._connection_info

            self.assertEqual(conn_info["host"], "localhost")
            self.assertEqual(conn_info["port"], 1414)
            self.assertEqual(conn_info["queue_manager"], "QM1")
            self.assertEqual(conn_info["channel"], "SYSTEM.DEF.SVRCONN")
            self.assertEqual(conn_info["timeout"], 30)

    def test_build_connection_info_defaults(self):
        """Test connection info building with defaults"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            config = {}
            adapter = MQLibraryAdapter(config, self.logger)
            conn_info = adapter._connection_info

            self.assertEqual(conn_info["host"], "localhost")
            self.assertEqual(conn_info["port"], 1414)

    def test_connect_success(self):
        """Test successful MQ connection"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_qmgr = Mock()
            self.mock_pymqi.connect.return_value = mock_qmgr

            adapter = MQLibraryAdapter(self.config, self.logger)
            result = adapter.connect()

            self.assertTrue(result)
            self.assertEqual(adapter._qmgr, mock_qmgr)
            self.logger.logger.info.assert_called()

    def test_connect_failure(self):
        """Test MQ connection failure"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            self.mock_pymqi.connect.side_effect = Exception("Connection failed")

            adapter = MQLibraryAdapter(self.config, self.logger)
            result = adapter.connect()

            self.assertFalse(result)
            self.logger.logger.error.assert_called()

    def test_disconnect_success(self):
        """Test successful disconnection"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_qmgr = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            adapter.disconnect()

            mock_qmgr.disconnect.assert_called_once()
            self.assertIsNone(adapter._qmgr)

    def test_disconnect_with_error(self):
        """Test disconnection with error"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_qmgr = Mock()
            mock_qmgr.disconnect.side_effect = Exception("Disconnect failed")

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            adapter.disconnect()

            self.logger.logger.error.assert_called()

    def test_is_connected_true(self):
        """Test is_connected returns True when connected"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            self.assertTrue(adapter.is_connected())

    def test_is_connected_false(self):
        """Test is_connected returns False when not connected"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = None

            self.assertFalse(adapter.is_connected())

    def test_is_connected_exception(self):
        """Test is_connected handles exceptions"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_qmgr = Mock()
            type(mock_qmgr).is_connected = PropertyMock(side_effect=Exception("Check failed"))

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            self.assertFalse(adapter.is_connected())

    def test_put_message_string(self):
        """Test putting string message"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            result = adapter.put_message("TEST.QUEUE", "test message")

            self.assertTrue(result)
            mock_queue.put.assert_called_once()
            mock_queue.close.assert_called_once()

    def test_put_message_dict(self):
        """Test putting dictionary message"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            result = adapter.put_message("TEST.QUEUE", {"key": "value"})

            self.assertTrue(result)

    def test_put_message_bytes(self):
        """Test putting bytes message"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            result = adapter.put_message("TEST.QUEUE", b"test bytes")

            self.assertTrue(result)

    def test_put_message_with_properties(self):
        """Test putting message with properties"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            mock_md = Mock()
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = mock_md

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            properties = {
                "correlation_id": "test_corr_id",
                "reply_to_queue": "REPLY.QUEUE",
                "message_type": 8,
                "priority": 5,
                "persistence": 1
            }

            result = adapter.put_message("TEST.QUEUE", "test", properties)

            self.assertTrue(result)
            self.assertEqual(mock_md.CorrelId, "test_corr_id")
            self.assertEqual(mock_md.ReplyToQ, "REPLY.QUEUE")

    def test_put_message_not_connected(self):
        """Test putting message when not connected"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            adapter = MQLibraryAdapter(self.config, self.logger)

            with self.assertRaises(Exception) as context:
                adapter.put_message("TEST.QUEUE", "test")
            self.assertIn("MQ connection not established", str(context.exception))

    def test_put_message_error(self):
        """Test putting message with error"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.put.side_effect = Exception("Put failed")
            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            result = adapter.put_message("TEST.QUEUE", "test")

            self.assertFalse(result)

    def test_get_message_success(self):
        """Test getting message successfully"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.get.return_value = b'{"key": "value"}'

            mock_md = Mock()
            mock_md.MsgId = b'\x01\x02\x03\x04'
            mock_md.CorrelId = b'\x05\x06\x07\x08'
            mock_md.ReplyToQ = b'REPLY.QUEUE         '
            mock_md.ReplyToQMgr = b'QM2                  '
            mock_md.MsgType = 8
            mock_md.Format = b'MQSTR   '
            mock_md.Priority = 5
            mock_md.Persistence = 1
            mock_md.Expiry = -1
            mock_md.PutTime = b'12345678'
            mock_md.PutDate = b'20240101'

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = mock_md
            self.mock_pymqi.GMO.return_value = Mock()
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQGMO_WAIT = 1
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            message = adapter.get_message("TEST.QUEUE")

            self.assertIsNotNone(message)
            self.assertEqual(message["data"]["key"], "value")

    def test_get_message_string(self):
        """Test getting string message"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.get.return_value = b'plain text message'

            mock_md = Mock()
            mock_md.MsgId = b'\x01\x02\x03\x04'
            mock_md.CorrelId = b''
            mock_md.ReplyToQ = b''
            mock_md.ReplyToQMgr = b''
            mock_md.MsgType = 8
            mock_md.Format = b'MQSTR   '
            mock_md.Priority = 0
            mock_md.Persistence = 1
            mock_md.Expiry = -1
            mock_md.PutTime = '12345678'
            mock_md.PutDate = '20240101'

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = mock_md
            self.mock_pymqi.GMO.return_value = Mock()
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQGMO_WAIT = 1
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            message = adapter.get_message("TEST.QUEUE")

            self.assertIsNotNone(message)
            self.assertEqual(message["data"], "plain text message")

    def test_get_message_no_message_available(self):
        """Test getting message when queue is empty"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mqmi_error = Exception("No message")
            mqmi_error.comp = self.mock_pymqi.CMQC.MQCC_FAILED
            mqmi_error.reason = self.mock_pymqi.CMQC.MQRC_NO_MSG_AVAILABLE
            mock_queue.get.side_effect = self.mock_pymqi.MQMIError(mqmi_error)

            self.mock_pymqi.MQMIError = type('MQMIError', (Exception,), {})
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQCC_FAILED = 2
            self.mock_pymqi.CMQC.MQRC_NO_MSG_AVAILABLE = 2033

            mock_error = self.mock_pymqi.MQMIError()
            mock_error.comp = 2
            mock_error.reason = 2033
            mock_queue.get.side_effect = mock_error

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()
            self.mock_pymqi.GMO.return_value = Mock()
            self.mock_pymqi.CMQC.MQGMO_WAIT = 1
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            message = adapter.get_message("TEST.QUEUE")

            self.assertIsNone(message)

    def test_get_message_error(self):
        """Test getting message with error"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.get.side_effect = Exception("Get failed")

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()
            self.mock_pymqi.GMO.return_value = Mock()
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQGMO_WAIT = 1
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            with self.assertRaises(Exception):
                adapter.get_message("TEST.QUEUE")

    def test_browse_message_success(self):
        """Test browsing message successfully"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.get.return_value = b'{"key": "value"}'

            mock_md = Mock()
            mock_md.MsgId = b'\x01\x02\x03\x04'
            mock_md.CorrelId = b''
            mock_md.ReplyToQ = b'REPLY.QUEUE         '
            mock_md.MsgType = 8
            mock_md.Format = b'MQSTR   '
            mock_md.Priority = 5
            mock_md.Persistence = 1

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = mock_md
            self.mock_pymqi.GMO.return_value = Mock()
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQOO_BROWSE = 8
            self.mock_pymqi.CMQC.MQGMO_BROWSE_FIRST = 16
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            message = adapter.browse_message("TEST.QUEUE")

            self.assertIsNotNone(message)
            self.assertEqual(message["data"]["key"], "value")

    def test_browse_message_with_message_id(self):
        """Test browsing specific message by ID"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.get.return_value = b'test message'

            mock_md = Mock()
            mock_md.MsgId = b'\x01\x02\x03\x04'
            mock_md.CorrelId = b''
            mock_md.ReplyToQ = b''
            mock_md.MsgType = 8
            mock_md.Format = b'MQSTR   '
            mock_md.Priority = 0
            mock_md.Persistence = 1

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = mock_md
            self.mock_pymqi.GMO.return_value = Mock()
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQOO_BROWSE = 8
            self.mock_pymqi.CMQC.MQGMO_BROWSE_FIRST = 16
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            message = adapter.browse_message("TEST.QUEUE", b'\x01\x02\x03\x04')

            self.assertIsNotNone(message)
            self.assertEqual(mock_md.MsgId, b'\x01\x02\x03\x04')

    def test_browse_message_no_message(self):
        """Test browsing when no message available"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()

            self.mock_pymqi.MQMIError = type('MQMIError', (Exception,), {})
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQCC_FAILED = 2
            self.mock_pymqi.CMQC.MQRC_NO_MSG_AVAILABLE = 2033
            self.mock_pymqi.CMQC.MQOO_BROWSE = 8
            self.mock_pymqi.CMQC.MQGMO_BROWSE_FIRST = 16
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            mock_error = self.mock_pymqi.MQMIError()
            mock_error.comp = 2
            mock_error.reason = 2033
            mock_queue.get.side_effect = mock_error

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()
            self.mock_pymqi.GMO.return_value = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            message = adapter.browse_message("TEST.QUEUE")

            self.assertIsNone(message)

    def test_browse_message_error(self):
        """Test browsing message with error"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.get.side_effect = Exception("Browse failed")

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()
            self.mock_pymqi.GMO.return_value = Mock()
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQOO_BROWSE = 8
            self.mock_pymqi.CMQC.MQGMO_BROWSE_FIRST = 16
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            with self.assertRaises(Exception):
                adapter.browse_message("TEST.QUEUE")

    def test_get_queue_depth_success(self):
        """Test getting queue depth successfully"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.inquire.return_value = 42

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQOO_INQUIRE = 32
            self.mock_pymqi.CMQC.MQIA_CURRENT_Q_DEPTH = 3

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            depth = adapter.get_queue_depth("TEST.QUEUE")

            self.assertEqual(depth, 42)

    def test_get_queue_depth_error(self):
        """Test getting queue depth with error"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.inquire.side_effect = Exception("Inquire failed")

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQOO_INQUIRE = 32
            self.mock_pymqi.CMQC.MQIA_CURRENT_Q_DEPTH = 3

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            depth = adapter.get_queue_depth("TEST.QUEUE")

            self.assertEqual(depth, -1)

    def test_purge_queue_success(self):
        """Test purging queue successfully"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()

            # Simulate 3 messages then no more messages
            self.mock_pymqi.MQMIError = type('MQMIError', (Exception,), {})
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQGMO_NO_WAIT = 4
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2
            self.mock_pymqi.CMQC.MQRC_NO_MSG_AVAILABLE = 2033

            no_msg_error = self.mock_pymqi.MQMIError()
            no_msg_error.reason = 2033

            mock_queue.get.side_effect = [b'msg1', b'msg2', b'msg3', no_msg_error]

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()
            self.mock_pymqi.GMO.return_value = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            count = adapter.purge_queue("TEST.QUEUE")

            self.assertEqual(count, 3)

    def test_purge_queue_error(self):
        """Test purging queue with error"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_queue = Mock()
            mock_queue.get.side_effect = Exception("Purge failed")

            mock_qmgr = Mock()
            mock_qmgr.is_connected = True
            self.mock_pymqi.Queue.return_value = mock_queue
            self.mock_pymqi.MD.return_value = Mock()
            self.mock_pymqi.GMO.return_value = Mock()
            self.mock_pymqi.CMQC = Mock()
            self.mock_pymqi.CMQC.MQGMO_NO_WAIT = 4
            self.mock_pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING = 2

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            with self.assertRaises(Exception):
                adapter.purge_queue("TEST.QUEUE")

    def test_test_connection_success(self):
        """Test connection test success"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            mock_pcf = Mock()
            mock_pcf.MQCMD_INQUIRE_Q_MGR.return_value = True
            self.mock_pymqi.PCFExecute.return_value = mock_pcf

            mock_qmgr = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            result = adapter.test_connection()

            self.assertTrue(result)

    def test_test_connection_no_qmgr(self):
        """Test connection test when no qmgr"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = None

            result = adapter.test_connection()

            self.assertFalse(result)

    def test_test_connection_failure(self):
        """Test connection test failure"""
        with patch('commonpython.adapters.mq_library_adapter.HAS_PYMQI', True):
            from commonpython.adapters.mq_library_adapter import MQLibraryAdapter

            self.mock_pymqi.PCFExecute.side_effect = Exception("Test failed")

            mock_qmgr = Mock()

            adapter = MQLibraryAdapter(self.config, self.logger)
            adapter._qmgr = mock_qmgr

            result = adapter.test_connection()

            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
