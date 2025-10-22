"""
Test cases for DB2Manager

Tests database functionality using CLI interface with mocked subprocess calls.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.database.db2_manager import DB2Manager


class TestDB2Manager(unittest.TestCase):
    """
    Test cases for DB2Manager class.

    @brief Comprehensive test suite for database functionality using CLI interface.
    """

    def setUp(self):
        """
        Set up test fixtures.

        @brief Initialize test environment before each test.
        """
        self.config = {
            "host": "localhost",
            "port": 50000,
            "database": "testdb",
            "user": "testuser",
            "password": "testpass",
            "schema": "testschema",
            "timeout": 30,
        }
        self.db_manager = DB2Manager(self.config)

    def test_init(self):
        """
        Test DB2Manager initialization.

        @brief Test that DB2Manager initializes correctly with configuration.
        """
        self.assertEqual(self.db_manager.config, self.config)
        self.assertIsNone(self.db_manager.logger)
        self.assertFalse(self.db_manager.connected)

    def test_init_with_logger(self):
        """
        Test DB2Manager initialization with logger.

        @brief Test DB2Manager initialization with logger instance.
        """
        mock_logger = MagicMock()
        db_manager = DB2Manager(self.config, mock_logger)
        self.assertEqual(db_manager.logger, mock_logger)

    def test_build_connection_string(self):
        """
        Test building connection string.

        @brief Test that connection string is built correctly from configuration.
        """
        conn_str = self.db_manager._build_connection_string()

        self.assertIn("DATABASE=testdb", conn_str)
        self.assertIn("HOSTNAME=localhost", conn_str)
        self.assertIn("PORT=50000", conn_str)
        self.assertIn("UID=testuser", conn_str)
        self.assertIn("PWD=testpass", conn_str)
        self.assertIn("CURRENTSCHEMA=testschema", conn_str)

    def test_build_connection_string_minimal(self):
        """
        Test building connection string with minimal configuration.

        @brief Test connection string building with minimal configuration.
        """
        minimal_config = {"database": "testdb"}
        db_manager = DB2Manager(minimal_config)
        conn_str = db_manager._build_connection_string()

        self.assertIn("DATABASE=testdb", conn_str)
        self.assertIn("HOSTNAME=localhost", conn_str)
        self.assertIn("PORT=50000", conn_str)
        self.assertIn("UID=db2inst1", conn_str)

    @patch("subprocess.run")
    def test_execute_db2_command_success(self, mock_run):
        """
        Test successful DB2 command execution.

        @brief Test that DB2 commands execute successfully.
        """
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = self.db_manager._execute_db2_command("connect to", ["testdb"])

        self.assertTrue(result["success"])
        self.assertEqual(result["stdout"], "Success")
        self.assertEqual(result["returncode"], 0)

    @patch("subprocess.run")
    def test_execute_db2_command_failure(self, mock_run):
        """
        Test DB2 command execution failure branch.
        """
        mock_run.side_effect = Exception("subprocess error")
        with self.assertRaises(Exception):
            self.db_manager._execute_db2_command("SELECT * FROM test")

    def test_connect_failure(self):
        """
        Test connect failure branch.
        """
        self.db_manager._build_connection_string = MagicMock(return_value=None)
        with patch.object(self.db_manager, "_execute_db2_command", side_effect=Exception("fail")):
            result = self.db_manager.connect()
            self.assertFalse(result)

    def test_disconnect_failure(self):
        """
        Test disconnect failure branch.
        """
        self.db_manager.connected = True
        with patch.object(self.db_manager, "_execute_db2_command", side_effect=Exception("fail")):
            self.db_manager.disconnect()  # Should not raise

    def test_execute_query_failure(self):
        """
        Test execute_query failure branch.
        """
        self.db_manager.connected = True
        with patch.object(self.db_manager, "_execute_db2_command", side_effect=Exception("fail")):
            with self.assertRaises(Exception):
                self.db_manager.execute_query("SELECT * FROM test")

    def test_execute_update_failure(self):
        """
        Test execute_update failure branch.
        """
        self.db_manager.connected = True
        with patch.object(self.db_manager, "_execute_db2_command", side_effect=Exception("fail")):
            with self.assertRaises(Exception):
                self.db_manager.execute_update("UPDATE test SET x=1")

    @patch("subprocess.run")
    def test_execute_db2_command_failure(self, mock_run):
        """
        Test failed DB2 command execution.

        @brief Test that failed DB2 commands are handled correctly.
        """
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Connection failed"
        mock_run.return_value = mock_result

        result = self.db_manager._execute_db2_command("connect to", ["testdb"])

        self.assertFalse(result["success"])
        self.assertEqual(result["stderr"], "Connection failed")
        self.assertEqual(result["returncode"], 1)

    @patch("subprocess.run")
    def test_execute_db2_command_timeout(self, mock_run):
        """
        Test DB2 command timeout.

        @brief Test that command timeouts are handled correctly.
        """
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("db2", 30)

        with self.assertRaises(Exception) as context:
            self.db_manager._execute_db2_command("connect to", ["testdb"])

        self.assertIn("timeout", str(context.exception))

    @patch("subprocess.run")
    def test_connect_success(self, mock_run):
        """
        Test successful database connection.

        @brief Test that database connection succeeds.
        """
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Connected"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = self.db_manager.connect()

        self.assertTrue(result)
        self.assertTrue(self.db_manager.connected)

    @patch("subprocess.run")
    def test_connect_failure(self, mock_run):
        """
        Test failed database connection.

        @brief Test that database connection failures are handled correctly.
        """
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Connection failed"
        mock_run.return_value = mock_result

        result = self.db_manager.connect()

        self.assertFalse(result)
        self.assertFalse(self.db_manager.connected)

    def test_disconnect(self):
        """
        Test database disconnection.

        @brief Test that database disconnection works correctly.
        """
        self.db_manager.connected = True

        with patch.object(self.db_manager, "_execute_db2_command") as mock_execute:
            self.db_manager.disconnect()

            mock_execute.assert_called_once_with("disconnect")
            self.assertFalse(self.db_manager.connected)

    def test_is_connected(self):
        """
        Test connection status check.

        @brief Test that connection status is checked correctly.
        """
        self.assertFalse(self.db_manager.is_connected())

        self.db_manager.connected = True
        self.assertTrue(self.db_manager.is_connected())

    @patch("subprocess.run")
    def test_execute_query_success(self, mock_run):
        """
        Test successful query execution.

        @brief Test that SELECT queries execute successfully.
        """
        self.db_manager.connected = True

        # Mock successful export command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Export successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Create a temporary CSV file for testing
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2\nvalue1,value2\nvalue3,value4\n")
            csv_file = f.name

        try:
            with patch.object(self.db_manager, "_parse_csv_results") as mock_parse:
                mock_parse.return_value = [{"col1": "value1", "col2": "value2"}]

                result = self.db_manager.execute_query("SELECT * FROM test")

                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]["col1"], "value1")
        finally:
            os.unlink(csv_file)

    def test_execute_query_not_connected(self):
        """
        Test query execution when not connected.

        @brief Test that queries fail when not connected to database.
        """
        with self.assertRaises(Exception) as context:
            self.db_manager.execute_query("SELECT * FROM test")

        self.assertIn("connection not established", str(context.exception))

    @patch("subprocess.run")
    def test_execute_update_success(self, mock_run):
        """
        Test successful update execution.

        @brief Test that DML queries execute successfully.
        """
        self.db_manager.connected = True

        # Mock successful import command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Import successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = self.db_manager.execute_update("INSERT INTO test VALUES (1)")

        self.assertEqual(result, 1)  # Default assumption

    def test_execute_update_not_connected(self):
        """
        Test update execution when not connected.

        @brief Test that updates fail when not connected to database.
        """
        with self.assertRaises(Exception) as context:
            self.db_manager.execute_update("INSERT INTO test VALUES (1)")

        self.assertIn("connection not established", str(context.exception))

    @patch("subprocess.run")
    def test_execute_batch_success(self, mock_run):
        """
        Test successful batch execution.

        @brief Test that batch queries execute successfully.
        """
        self.db_manager.connected = True

        # Mock successful commands
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(self.db_manager, "execute_update") as mock_execute:
            mock_execute.return_value = 1

            queries = ["INSERT INTO test VALUES (1)", "UPDATE test SET col = 2"]
            result = self.db_manager.execute_batch(queries)

            self.assertEqual(len(result), 2)
            self.assertEqual(result, [1, 1])

    def test_execute_batch_not_connected(self):
        """
        Test batch execution when not connected.

        @brief Test that batch operations fail when not connected to database.
        """
        with self.assertRaises(Exception) as context:
            self.db_manager.execute_batch(["INSERT INTO test VALUES (1)"])

        self.assertIn("connection not established", str(context.exception))

    def test_transaction_context_manager(self):
        """
        Test transaction context manager.

        @brief Test that transaction context manager works correctly.
        """
        self.db_manager.connected = True

        with patch.object(self.db_manager, "_execute_db2_command") as mock_execute:
            with self.db_manager.transaction():
                pass

            # Should call begin and commit
            self.assertEqual(mock_execute.call_count, 2)
            mock_execute.assert_any_call("begin transaction")
            mock_execute.assert_any_call("commit")

    def test_transaction_context_manager_with_exception(self):
        """
        Test transaction context manager with exception.

        @brief Test that transaction context manager handles exceptions correctly.
        """
        self.db_manager.connected = True

        with patch.object(self.db_manager, "_execute_db2_command") as mock_execute:
            with self.assertRaises(ValueError):
                with self.db_manager.transaction():
                    raise ValueError("Test error")

            # Should call begin and rollback (no commit on exception)
            self.assertEqual(mock_execute.call_count, 2)
            mock_execute.assert_any_call("begin transaction")
            mock_execute.assert_any_call("rollback")

    def test_transaction_context_manager_not_connected(self):
        """
        Test transaction context manager when not connected.

        @brief Test that transaction context manager fails when not connected.
        """
        with self.assertRaises(Exception) as context:
            with self.db_manager.transaction():
                pass

        self.assertIn("connection not established", str(context.exception))

    @patch("subprocess.run")
    def test_get_table_info(self, mock_run):
        """
        Test getting table information.

        @brief Test that table information is retrieved correctly.
        """
        self.db_manager.connected = True

        # Mock successful export command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Export successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(self.db_manager, "execute_query") as mock_execute:
            mock_execute.return_value = [{"COLNAME": "id", "TYPENAME": "INTEGER"}]

            result = self.db_manager.get_table_info("test_table")

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["COLNAME"], "id")

    @patch("subprocess.run")
    def test_get_database_info(self, mock_run):
        """
        Test getting database information.

        @brief Test that database information is retrieved correctly.
        """
        self.db_manager.connected = True

        # Mock successful export command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Export successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(self.db_manager, "execute_query") as mock_execute:
            mock_execute.return_value = [{"INST_NAME": "test_instance"}]

            result = self.db_manager.get_database_info()

            self.assertEqual(result["INST_NAME"], "test_instance")

    @patch("subprocess.run")
    def test_test_connection_success(self, mock_run):
        """
        Test successful connection test.

        @brief Test that connection testing works correctly.
        """
        self.db_manager.connected = True

        # Mock successful export command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Export successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with patch.object(self.db_manager, "execute_query") as mock_execute:
            mock_execute.return_value = [{"1": 1}]

            result = self.db_manager.test_connection()

            self.assertTrue(result)

    def test_parse_csv_results(self):
        """
        Test CSV results parsing.

        @brief Test that CSV results are parsed correctly.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2\nvalue1,value2\nvalue3,value4\n")
            csv_file = f.name

        try:
            result = self.db_manager._parse_csv_results(csv_file)

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["col1"], "value1")
            self.assertEqual(result[0]["col2"], "value2")
            self.assertEqual(result[1]["col1"], "value3")
            self.assertEqual(result[1]["col2"], "value4")
        finally:
            os.unlink(csv_file)

    def test_parse_csv_results_empty(self):
        """
        Test CSV results parsing with empty file.

        @brief Test that empty CSV files are handled correctly.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            csv_file = f.name

        try:
            result = self.db_manager._parse_csv_results(csv_file)
            self.assertEqual(len(result), 0)
        finally:
            os.unlink(csv_file)

    def test_execute_query_finally_cleanup(self):
        """
        @brief Test execute_query cleans up temp files in finally block.
        """
        self.db_manager.connected = True
        with patch.object(self.db_manager, "_execute_db2_command") as mock_exec:
            mock_exec.side_effect = [
                MagicMock(success=True, stdout="", stderr="", returncode=0),
                MagicMock(success=True, stdout="", stderr="", returncode=0),
            ]
            with patch("os.unlink") as mock_unlink:
                with patch("builtins.open", mock_open(read_data="col1,col2\nval1,val2\n")):
                    with patch.object(
                        self.db_manager,
                        "_parse_csv_results",
                        return_value=[{"col1": "val1", "col2": "val2"}],
                    ):
                        result = self.db_manager.execute_query("SELECT * FROM test")
                        mock_unlink.assert_called()
                        self.assertEqual(result, [{"col1": "val1", "col2": "val2"}])

    def test_execute_update_finally_cleanup(self):
        """
        @brief Test execute_update cleans up temp files in finally block.
        """
        self.db_manager.connected = True
        with patch.object(
            self.db_manager,
            "_execute_db2_command",
            return_value=MagicMock(success=True, stdout="", stderr="", returncode=0),
        ):
            with patch("os.unlink") as mock_unlink:
                result = self.db_manager.execute_update("UPDATE test SET x=1")
                mock_unlink.assert_called()
                self.assertEqual(result, 1)

    def test_execute_query_csv_parse_error(self):
        """
        @brief Test error branch in _parse_csv_results.
        """
        with patch("builtins.open", side_effect=Exception("fail")):
            result = self.db_manager._parse_csv_results("fake.csv")
            self.assertEqual(result, [])

    def test_execute_db2_command_logger_error(self):
        """
        @brief Test _execute_db2_command with logger raising error.
        """
        db_manager = DB2Manager(self.config, MagicMock())
        db_manager.logger.logger.error.side_effect = Exception("Logger fail")
        with patch("subprocess.run", side_effect=Exception("subprocess error")):
            with self.assertRaises(Exception):
                db_manager._execute_db2_command("SELECT * FROM test")

    def test_execute_db2_command_no_logger(self):
        """
        @brief Test _execute_db2_command with no logger present.
        """
        db_manager = DB2Manager(self.config)
        with patch("subprocess.run", side_effect=Exception("subprocess error")):
            with self.assertRaises(Exception):
                db_manager._execute_db2_command("SELECT * FROM test")

    def test_execute_query_csv_result_missing_file(self):
        """
        @brief Test _parse_csv_results with missing file.
        """
        db_manager = DB2Manager(self.config)
        with patch("builtins.open", side_effect=FileNotFoundError()):
            result = db_manager._parse_csv_results("missing.csv")
            self.assertEqual(result, [])
