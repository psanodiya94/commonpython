"""
Test cases for CLI

Tests command-line interface functionality using only standard Python modules.
"""

import unittest
import tempfile
import os
import sys
import json
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import argparse

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.cli.cli import CLI, create_parser, main


class TestCLI(unittest.TestCase):
	"""
	Test cases for CLI class.
	
	@brief Comprehensive test suite for command-line interface functionality.
	"""

	def setUp(self):
		"""
		Set up test fixtures.

		@brief Initialize test environment before each test.
		"""
		# Create a temporary config file with required sections
		with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
			import yaml
			test_config = {
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
					'file': 'test.log',
					'dir': 'log',
					'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					'max_size': 10485760,
					'backup_count': 5,
					'colored': True,
					'json_format': False
				}
			}
			yaml.dump(test_config, f)
			self.config_file = f.name
		
		self.cli = CLI(self.config_file)
		
		# Mock the manager objects
		self.cli.db_manager = MagicMock()
		self.cli.mq_manager = MagicMock()
		self.cli.config_manager = MagicMock()
	
	def tearDown(self):
		"""
		Clean up test fixtures.
		
		@brief Clean up test environment after each test.
		"""
		if hasattr(self, 'config_file') and self.config_file and os.path.exists(self.config_file):
			os.unlink(self.config_file)
	
	def test_init(self):
		"""
		Test CLI initialization.
		
		@brief Test that CLI initializes correctly.
		"""
		self.assertIsNotNone(self.cli.config_manager)
		self.assertIsNotNone(self.cli.logger_manager)
		self.assertIsNotNone(self.cli.db_manager)
		self.assertIsNotNone(self.cli.mq_manager)
	
	def test_init_with_config_file(self):
		"""
		Test CLI initialization with config file.
		
		@brief Test CLI initialization with configuration file.
		"""
		with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
			import yaml
			yaml.dump({'logging': {'dir': 'log'}}, f)
			config_file = f.name
		
		try:
			cli = CLI(config_file)
			self.assertEqual(cli.config_file, config_file)
		finally:
			os.unlink(config_file)
	
	def test_init_without_config_file(self):
		"""
		Test CLI initialization without config file.
		"""
		cli = CLI(None)
		self.assertIsNone(cli.config_file)
		self.assertIsNotNone(cli.config_manager)
	
	@patch('sys.exit')
	def test_initialize_components_import_error(self, mock_exit):
		"""
		Test _initialize_components with import error.
		"""
		with patch('builtins.__import__', side_effect=ImportError("Module not found")):
			with patch('builtins.print') as mock_print:
				cli = CLI.__new__(CLI)
				cli.config_file = None
				cli._initialize_components()
				mock_exit.assert_called_with(1)

	@patch('commonpython.database.db2_manager.DB2Manager')
	@patch('commonpython.config.config_manager.ConfigManager')
	@patch('commonpython.logging.logger_manager.LoggerManager')
	def test_setup_database_success(self, mock_logger_manager_class, mock_config_manager_class, mock_db_manager_class):
		"""
		Test successful database setup.
		
		@brief Test that database setup succeeds.
		"""
		mock_db_manager = MagicMock()
		mock_db_manager_class.return_value = mock_db_manager
		mock_logger_manager = MagicMock()
		mock_logger_manager_class.return_value = mock_logger_manager
		mock_config_manager = MagicMock()
		mock_config_manager.get_database_config.return_value = {'host': 'localhost'}
		mock_config_manager.get_logging_config.return_value = {}
		mock_config_manager_class.return_value = mock_config_manager
		
		cli = CLI(self.config_file)
		cli.db_manager = mock_db_manager
		mock_db_manager.connect.return_value = True
		
		result = cli._setup_database()
		
		self.assertTrue(result)
		self.assertIs(cli.db_manager, mock_db_manager)
		mock_db_manager.connect.assert_called_once()
	
	@patch('commonpython.database.db2_manager.DB2Manager')
	@patch('commonpython.config.config_manager.ConfigManager')
	@patch('commonpython.logging.logger_manager.LoggerManager')
	def test_setup_database_failure(self, mock_logger_manager_class, mock_config_manager_class, mock_db_manager_class):
		"""
		Test failed database setup.
		
		@brief Test that database setup failures are handled correctly.
		"""
		mock_db_manager = MagicMock()
		mock_db_manager_class.return_value = mock_db_manager
		mock_logger_manager = MagicMock()
		mock_logger_manager_class.return_value = mock_logger_manager
		mock_config_manager = MagicMock()
		mock_config_manager.get_database_config.return_value = {'host': 'localhost'}
		mock_config_manager.get_logging_config.return_value = {}
		mock_config_manager_class.return_value = mock_config_manager
		
		cli = CLI(self.config_file)
		cli.db_manager = mock_db_manager
		mock_db_manager.connect.side_effect = Exception("Connection failed")
		
		with patch('builtins.print') as mock_print:
			result = cli._setup_database()
			
			self.assertFalse(result)
			mock_print.assert_called()
	
	def test_setup_database_connect_returns_false(self):
		"""
		Test setup database when connect returns False.
		"""
		self.cli.db_manager.connect.return_value = False
		result = self.cli._setup_database()
		self.assertFalse(result)
	
	@patch('commonpython.messaging.mq_manager.MQManager')
	@patch('commonpython.config.config_manager.ConfigManager')
	@patch('commonpython.logging.logger_manager.LoggerManager')
	def test_setup_messaging_success(self, mock_logger_manager_class, mock_config_manager_class, mock_mq_manager_class):
		"""
		Test successful messaging setup.
		
		@brief Test that messaging setup succeeds.
		"""
		mock_mq_manager = MagicMock()
		mock_mq_manager_class.return_value = mock_mq_manager
		mock_logger_manager = MagicMock()
		mock_logger_manager_class.return_value = mock_logger_manager
		mock_config_manager = MagicMock()
		mock_config_manager.get_messaging_config.return_value = {'host': 'localhost'}
		mock_config_manager.get_logging_config.return_value = {}
		mock_config_manager_class.return_value = mock_config_manager
		
		cli = CLI(self.config_file)
		cli.mq_manager = mock_mq_manager
		mock_mq_manager.connect.return_value = True
		
		result = cli._setup_messaging()
		
		self.assertTrue(result)
		self.assertIs(cli.mq_manager, mock_mq_manager)
		mock_mq_manager.connect.assert_called_once()
	
	@patch('commonpython.messaging.mq_manager.MQManager')
	@patch('commonpython.config.config_manager.ConfigManager')
	@patch('commonpython.logging.logger_manager.LoggerManager')
	def test_setup_messaging_failure(self, mock_logger_manager_class, mock_config_manager_class, mock_mq_manager_class):
		"""
		Test failed messaging setup.
		
		@brief Test that messaging setup failures are handled correctly.
		"""
		mock_mq_manager = MagicMock()
		mock_mq_manager_class.return_value = mock_mq_manager
		mock_logger_manager = MagicMock()
		mock_logger_manager_class.return_value = mock_logger_manager
		mock_config_manager = MagicMock()
		mock_config_manager.get_messaging_config.return_value = {'host': 'localhost'}
		mock_config_manager.get_logging_config.return_value = {}
		mock_config_manager_class.return_value = mock_config_manager
		
		cli = CLI(self.config_file)
		cli.mq_manager = mock_mq_manager
		mock_mq_manager.connect.side_effect = Exception("Connection failed")
		
		with patch('builtins.print') as mock_print:
			result = cli._setup_messaging()
			
			self.assertFalse(result)
			mock_print.assert_called()
	
	def test_setup_messaging_connect_returns_false(self):
		"""
		Test setup messaging when connect returns False.
		"""
		self.cli.mq_manager.connect.return_value = False
		result = self.cli._setup_messaging()
		self.assertFalse(result)
	
	def test_display_results_empty(self):
		"""
		Test displaying empty results.
		
		@brief Test that empty results are displayed correctly.
		"""
		with patch('builtins.print') as mock_print:
			self.cli._display_results([], "Test Results")
			mock_print.assert_called_with("No test results found")
	
	def test_display_results_none(self):
		"""
		Test displaying None results.
		"""
		with patch('builtins.print') as mock_print:
			self.cli._display_results(None, "Test Results")
			mock_print.assert_called_with("No test results found")
	
	def test_display_results_list_of_dicts(self):
		"""
		Test displaying list of dictionaries.
		
		@brief Test that list of dictionaries is displayed as a table.
		"""
		results = [
			{'name': 'John', 'age': 30},
			{'name': 'Jane', 'age': 25}
		]
		
		with patch('builtins.print') as mock_print:
			self.cli._display_results(results, "Test Results")
			
			# Should print header and rows
			self.assertGreaterEqual(mock_print.call_count, 3)
	
	def test_display_results_single_dict(self):
		"""
		Test displaying single dictionary (not in list).
		"""
		results = {'key': 'value', 'number': 123}
		
		with patch('builtins.print') as mock_print:
			self.cli._display_results(results, "Test Results")
			mock_print.assert_called()
	
	def test_display_results_list_with_empty_dict(self):
		"""
		Test displaying list containing empty dict.
		"""
		results = [{}]
		
		with patch('builtins.print') as mock_print:
			self.cli._display_results(results, "Test Results")
			mock_print.assert_called()
	
	def test_display_results_list_of_strings(self):
		"""
		Test displaying list of strings.
		"""
		results = ['item1', 'item2', 'item3']
		
		with patch('builtins.print') as mock_print:
			self.cli._display_results(results, "Test Results")
			mock_print.assert_called()
	
	@patch.object(CLI, '_setup_database')
	def test_test_database_success(self, mock_setup):
		"""
		Test successful database testing.
		
		@brief Test that database testing succeeds.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.test_connection.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.test_database()
			
			calls = [call("Testing database connection..."), call("✓ Database connection successful")]
			mock_print.assert_has_calls(calls)
	
	@patch.object(CLI, '_setup_database')
	def test_test_database_failure(self, mock_setup):
		"""
		Test failed database testing.
		
		@brief Test that database testing failures are handled correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.test_connection.return_value = False
		
		with patch('builtins.print') as mock_print:
			self.cli.test_database()
			
			mock_print.assert_called_with("✗ Database connection failed")
	
	@patch.object(CLI, '_setup_database')
	def test_test_database_setup_failure(self, mock_setup):
		"""
		Test database testing with setup failure.
		
		@brief Test that database testing handles setup failures correctly.
		"""
		mock_setup.return_value = False
		
		with patch('builtins.print') as mock_print:
			self.cli.test_database()
			
			mock_print.assert_called_with("✗ Database setup failed")
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_select(self, mock_setup):
		"""
		Test executing SELECT query.
		
		@brief Test that SELECT queries are executed correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.execute_query.return_value = [{'id': 1, 'name': 'test'}]
		
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.execute_query("SELECT * FROM test")
			
			self.cli.db_manager.execute_query.assert_called_once_with("SELECT * FROM test", None)
			mock_display.assert_called_once()
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_select_lowercase(self, mock_setup):
		"""
		Test executing select query in lowercase.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.execute_query.return_value = [{'id': 1}]
		
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.execute_query("select * from test")
			
			self.cli.db_manager.execute_query.assert_called_once()
			mock_display.assert_called_once()
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_update(self, mock_setup):
		"""
		Test executing UPDATE query.
		
		@brief Test that UPDATE queries are executed correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.execute_update.return_value = 1
		
		with patch('builtins.print') as mock_print:
			self.cli.execute_query("UPDATE test SET col = 1")
			
			self.cli.db_manager.execute_update.assert_called_once_with("UPDATE test SET col = 1", None)
			mock_print.assert_called_with("Query executed successfully. Rows affected: 1")
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_insert(self, mock_setup):
		"""
		Test executing INSERT query.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.execute_update.return_value = 1
		
		with patch('builtins.print') as mock_print:
			self.cli.execute_query("INSERT INTO test VALUES (1)")
			
			self.cli.db_manager.execute_update.assert_called_once()
			mock_print.assert_called()
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_delete(self, mock_setup):
		"""
		Test executing DELETE query.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.execute_update.return_value = 5
		
		with patch('builtins.print') as mock_print:
			self.cli.execute_query("DELETE FROM test WHERE id = 1")
			
			self.cli.db_manager.execute_update.assert_called_once()
			mock_print.assert_called_with("Query executed successfully. Rows affected: 5")
	
	@patch('sys.exit')
	@patch.object(CLI, '_setup_database')
	def test_execute_query_setup_failure(self, mock_setup, mock_exit):
		"""
		Test query execution with setup failure.
		
		@brief Test that query execution handles setup failures correctly.
		"""
		mock_setup.return_value = False
		
		self.cli.execute_query("SELECT * FROM test")
		
		mock_exit.assert_called_with(1)
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_with_params(self, mock_setup):
		"""
		Test executing query with parameters.
		
		@brief Test that queries with parameters are executed correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.execute_query.return_value = [{'id': 1}]
		
		with patch.object(self.cli, '_display_results'):
			self.cli.execute_query("SELECT * FROM test WHERE id = ?", '["1"]')
			
			self.cli.db_manager.execute_query.assert_called_once_with("SELECT * FROM test WHERE id = ?", ("1",))
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_with_multiple_params(self, mock_setup):
		"""
		Test executing query with multiple parameters.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.execute_query.return_value = [{'id': 1}]
		
		with patch.object(self.cli, '_display_results'):
			self.cli.execute_query("SELECT * FROM test WHERE id = ? AND name = ?", '["1", "test"]')
			
			self.cli.db_manager.execute_query.assert_called_once_with(
				"SELECT * FROM test WHERE id = ? AND name = ?", 
				("1", "test")
			)
	
	@patch('sys.exit')
	@patch.object(CLI, '_setup_database')
	def test_execute_query_invalid_json_params(self, mock_setup, mock_exit):
		"""
		Test executing query with invalid JSON parameters.
		"""
		mock_setup.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.execute_query("SELECT * FROM test WHERE id = ?", '{invalid json}')
			
			mock_exit.assert_called_with(1)
	
	@patch('sys.exit')
	def test_execute_query_exception(self, mock_exit):
		"""
		Test execute_query exits on exception.
		"""
		self.cli._setup_database = MagicMock(return_value=True)
		self.cli.db_manager.execute_query = MagicMock(side_effect=Exception('Database error'))
		
		with patch('builtins.print') as mock_print:
			self.cli.execute_query('SELECT * FROM test')
			
			mock_exit.assert_called_once_with(1)
			mock_print.assert_called()
	
	@patch.object(CLI, '_setup_database')
	def test_get_table_info(self, mock_setup):
		"""
		Test getting table information.
		
		@brief Test that table information is retrieved correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager.get_table_info.return_value = [{'COLNAME': 'id', 'TYPENAME': 'INTEGER'}]
		
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.get_table_info("test_table")
			
			self.cli.db_manager.get_table_info.assert_called_once_with("test_table")
			mock_display.assert_called_once()
	
	@patch('sys.exit')
	@patch.object(CLI, '_setup_database')
	def test_get_table_info_setup_fail(self, mock_setup, mock_exit):
		"""
		@brief Test get_table_info exits if setup fails.
		"""
		mock_setup.return_value = False
		
		self.cli.get_table_info('table')
		
		mock_exit.assert_called_with(1)
	
	@patch('sys.exit')
	def test_get_table_info_exception(self, mock_exit):
		"""
		Test get_table_info exits on exception.
		"""
		self.cli._setup_database = MagicMock(return_value=True)
		self.cli.db_manager.get_table_info = MagicMock(side_effect=Exception('Database error'))
		
		with patch('builtins.print') as mock_print:
			self.cli.get_table_info('table')
			
			mock_exit.assert_called_once_with(1)
			mock_print.assert_called()
	
	@patch.object(CLI, '_setup_messaging')
	def test_test_messaging_success(self, mock_setup):
		"""
		Test successful messaging testing.
		
		@brief Test that messaging testing succeeds.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.test_connection.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.test_messaging()
			
			calls = [call("Testing MQ connection..."), call("✓ MQ connection successful")]
			mock_print.assert_has_calls(calls)
	
	@patch.object(CLI, '_setup_messaging')
	def test_test_messaging_failure(self, mock_setup):
		"""
		Test failed messaging testing.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.test_connection.return_value = False
		
		with patch('builtins.print') as mock_print:
			self.cli.test_messaging()
			
			mock_print.assert_called_with("✗ MQ connection failed")
	
	@patch.object(CLI, '_setup_messaging')
	def test_test_messaging_setup_failure(self, mock_setup):
		"""
		Test messaging testing with setup failure.
		"""
		mock_setup.return_value = False
		
		with patch('builtins.print') as mock_print:
			self.cli.test_messaging()
			
			mock_print.assert_called_with("✗ MQ setup failed")
	
	@patch.object(CLI, '_setup_messaging')
	def test_get_message_success(self, mock_setup):
		"""
		Test successful message retrieval.
		
		@brief Test that messages are retrieved successfully.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.get_message.return_value = {'data': 'test message'}
		
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.get_message("TEST.QUEUE")
			
			self.cli.mq_manager.get_message.assert_called_once_with("TEST.QUEUE", None)
			mock_display.assert_called_once()
	
	@patch.object(CLI, '_setup_messaging')
	def test_get_message_with_timeout(self, mock_setup):
		"""
		Test message retrieval with timeout.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.get_message.return_value = {'data': 'test message'}
		
		with patch.object(self.cli, '_display_results'):
			self.cli.get_message("TEST.QUEUE", timeout=10)
			
			self.cli.mq_manager.get_message.assert_called_once_with("TEST.QUEUE", 10)
	
	@patch.object(CLI, '_setup_messaging')
	def test_get_message_no_message(self, mock_setup):
		"""
		Test message retrieval when no message available.
		
		@brief Test that no message case is handled correctly.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.get_message.return_value = None
		
		with patch('builtins.print') as mock_print:
			self.cli.get_message("TEST.QUEUE")
			
			mock_print.assert_called_with("No message available in queue TEST.QUEUE")
	
	@patch('sys.exit')
	@patch.object(CLI, '_setup_messaging')
	def test_get_message_setup_fail(self, mock_setup, mock_exit):
		"""
		@brief Test get_message exits if setup fails.
		"""
		mock_setup.return_value = False
		
		self.cli.get_message('Q')
		
		mock_exit.assert_called_with(1)
	
	@patch('sys.exit')
	def test_get_message_exception(self, mock_exit):
		"""
		Test get_message exits on exception.
		"""
		self.cli._setup_messaging = MagicMock(return_value=True)
		self.cli.mq_manager.get_message = MagicMock(side_effect=Exception('MQ error'))
		
		with patch('builtins.print') as mock_print:
			self.cli.get_message('Q')
			
			mock_exit.assert_called_once_with(1)
			mock_print.assert_called()
	
	@patch.object(CLI, '_setup_messaging')
	def test_put_message_success(self, mock_setup):
		"""
		Test successful message sending.
		
		@brief Test that messages are sent successfully.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.put_message.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.put_message("TEST.QUEUE", "test message")
			
			self.cli.mq_manager.put_message.assert_called_once()
			mock_print.assert_called_with("Message sent to queue TEST.QUEUE")
	
	@patch.object(CLI, '_setup_messaging')
	def test_put_message_with_json_string(self, mock_setup):
		"""
		Test sending message with JSON string.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.put_message.return_value = True
		
		with patch('builtins.print'):
			self.cli.put_message("TEST.QUEUE", '{"key": "value"}')
			
			# Should parse JSON and pass dict
			args = self.cli.mq_manager.put_message.call_args[0]
			self.assertIsInstance(args[1], dict)
	
	@patch.object(CLI, '_setup_messaging')
	def test_put_message_with_properties(self, mock_setup):
		"""
		Test sending message with properties.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.put_message.return_value = True
		
		with patch('builtins.print'):
			self.cli.put_message("TEST.QUEUE", "test message", '{"priority": 5}')
			
			self.cli.mq_manager.put_message.assert_called_once()
	
	@patch.object(CLI, '_setup_messaging')
	def test_put_message_with_invalid_properties_json(self, mock_setup):
		"""
		Test sending message with invalid properties JSON.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.put_message.return_value = True
		
		with patch('builtins.print'):
			self.cli.put_message("TEST.QUEUE", "test message", '{invalid json}')
			
			# Should handle invalid JSON gracefully
			self.cli.mq_manager.put_message.assert_called_once()
	
	@patch('sys.exit')
	@patch.object(CLI, '_setup_messaging')
	def test_put_message_failure(self, mock_setup, mock_exit):
		"""
		Test failed message sending.
		
		@brief Test that message sending failures are handled correctly.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.put_message.return_value = False
		
		with patch('builtins.print') as mock_print:
			self.cli.put_message("TEST.QUEUE", "test message")
			
			mock_exit.assert_called_with(1)
			mock_print.assert_called()
	
	@patch('sys.exit')
	@patch.object(CLI, '_setup_messaging')
	def test_put_message_setup_fail(self, mock_setup, mock_exit):
		"""
		@brief Test put_message exits if setup fails.
		"""
		mock_setup.return_value = False
		
		self.cli.put_message('Q', 'msg')
		
		mock_exit.assert_called_with(1)
	
	@patch('sys.exit')
	def test_put_message_exception(self, mock_exit):
		"""
		Test put_message exits on exception.
		"""
		self.cli._setup_messaging = MagicMock(return_value=True)
		self.cli.mq_manager.put_message = MagicMock(side_effect=Exception('MQ error'))
		
		with patch('builtins.print') as mock_print:
			self.cli.put_message('Q', 'msg')
			
			mock_exit.assert_called_once_with(1)
			mock_print.assert_called()
	
	@patch.object(CLI, '_setup_messaging')
	def test_get_queue_depth(self, mock_setup):
		"""
		Test getting queue depth.
		
		@brief Test that queue depth is retrieved correctly.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.get_queue_depth.return_value = 5
		
		with patch('builtins.print') as mock_print:
			self.cli.get_queue_depth("TEST.QUEUE")
			
			self.cli.mq_manager.get_queue_depth.assert_called_once_with("TEST.QUEUE")
			mock_print.assert_called_with("Queue TEST.QUEUE depth: 5")
	
	@patch.object(CLI, '_setup_messaging')
	def test_get_queue_depth_zero(self, mock_setup):
		"""
		Test getting queue depth when zero.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.get_queue_depth.return_value = 0
		
		with patch('builtins.print') as mock_print:
			self.cli.get_queue_depth("TEST.QUEUE")
			
			mock_print.assert_called_with("Queue TEST.QUEUE depth: 0")
	
	@patch('sys.exit')
	@patch.object(CLI, '_setup_messaging')
	def test_get_queue_depth_negative(self, mock_setup, mock_exit):
		"""
		Test getting queue depth when negative (error).
		"""
		mock_setup.return_value = True
		self.cli.mq_manager.get_queue_depth.return_value = -1
		
		with patch('builtins.print') as mock_print:
			self.cli.get_queue_depth("TEST.QUEUE")
			
			mock_exit.assert_called_with(1)
			mock_print.assert_called_with("Failed to get queue depth")
	
	@patch('sys.exit')
	@patch.object(CLI, '_setup_messaging')
	def test_get_queue_depth_setup_fail(self, mock_setup, mock_exit):
		"""
		@brief Test get_queue_depth exits if setup fails.
		"""
		mock_setup.return_value = False
		
		self.cli.get_queue_depth('Q')
		
		mock_exit.assert_called_with(1)
	
	@patch('sys.exit')
	def test_get_queue_depth_exception(self, mock_exit):
		"""
		Test get_queue_depth exits on exception.
		"""
		self.cli._setup_messaging = MagicMock(return_value=True)
		self.cli.mq_manager.get_queue_depth = MagicMock(side_effect=Exception('MQ error'))
		
		with patch('builtins.print') as mock_print:
			self.cli.get_queue_depth('Q')
			
			mock_exit.assert_called_once_with(1)
			mock_print.assert_called()
	
	def test_show_config(self):
		"""
		Test showing configuration.
		
		@brief Test that configuration is displayed correctly.
		"""
		self.cli.config_manager.to_dict.return_value = {'key': 'value'}
		
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.show_config()
			
			mock_display.assert_called_once()
			self.assertEqual(mock_display.call_args[0][0], {'key': 'value'})
	
	def test_get_config(self):
		"""
		Test getting configuration value.
		
		@brief Test that configuration values are retrieved correctly.
		"""
		self.cli.config_manager.get.return_value = 'test_value'
		
		with patch('builtins.print') as mock_print:
			self.cli.get_config('test.key')
			
			self.cli.config_manager.get.assert_called_once_with('test.key')
			mock_print.assert_called_with("test.key: test_value")
	
	def test_get_config_none_value(self):
		"""
		Test getting configuration value that returns None.
		"""
		self.cli.config_manager.get.return_value = None
		
		with patch('builtins.print') as mock_print:
			self.cli.get_config('nonexistent.key')
			
			mock_print.assert_called_with("nonexistent.key: None")
	
	def test_set_config(self):
		"""
		Test setting configuration value.
		
		@brief Test that configuration values are set correctly.
		"""
		with patch('builtins.print') as mock_print:
			self.cli.set_config('test.key', 'test_value')
			
			self.cli.config_manager.set.assert_called_once_with('test.key', 'test_value')
			mock_print.assert_called_with("Set test.key = test_value")
	
	def test_set_config_numeric_value(self):
		"""
		Test setting configuration with numeric value.
		"""
		with patch('builtins.print') as mock_print:
			self.cli.set_config('test.port', '8080')
			
			self.cli.config_manager.set.assert_called_once_with('test.port', '8080')
	
	def test_test_all(self):
		"""
		Test test_all method.
		"""
		self.cli._setup_database = MagicMock(return_value=True)
		self.cli._setup_messaging = MagicMock(return_value=True)
		self.cli.db_manager.test_connection.return_value = True
		self.cli.mq_manager.test_connection.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.test_all()
			
			# Verify all components were tested
			self.cli._setup_database.assert_called_once()
			self.cli._setup_messaging.assert_called_once()
			self.cli.db_manager.test_connection.assert_called_once()
			self.cli.mq_manager.test_connection.assert_called_once()
	
	def test_test_all_database_fail(self):
		"""
		Test test_all when database fails.
		"""
		self.cli._setup_database = MagicMock(return_value=False)
		self.cli._setup_messaging = MagicMock(return_value=True)
		self.cli.mq_manager.test_connection.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.test_all()
			
			# Should still test messaging even if database fails
			self.cli._setup_messaging.assert_called_once()
	
	def test_test_all_messaging_fail(self):
		"""
		Test test_all when messaging fails.
		"""
		self.cli._setup_database = MagicMock(return_value=True)
		self.cli._setup_messaging = MagicMock(return_value=False)
		self.cli.db_manager.test_connection.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.test_all()
			
			# Should test both even if one fails
			self.cli._setup_database.assert_called_once()
			self.cli._setup_messaging.assert_called_once()


class TestCreateParser(unittest.TestCase):
	"""
	Test cases for create_parser function.
    
	@brief Test suite for argument parser creation.
	"""
	
	def test_create_parser(self):
		"""
		Test parser creation.
        
		@brief Test that argument parser is created correctly.
		"""
		parser = create_parser()
		self.assertIsInstance(parser, argparse.ArgumentParser)
	
	def test_parser_has_config_option(self):
		"""
		Test parser has config option.
		"""
		parser = create_parser()
		args = parser.parse_args(['--config', 'test.yaml', 'test-all'])
		self.assertEqual(args.config, 'test.yaml')
	
	def test_parser_config_short_option(self):
		"""
		Test parser config short option.
		"""
		parser = create_parser()
		args = parser.parse_args(['-c', 'test.yaml', 'test-all'])
		self.assertEqual(args.config, 'test.yaml')
	
	def test_parser_database_subcommands(self):
		"""
		Test that parser has database subcommands.
		"""
		parser = create_parser()
		
		args = parser.parse_args(['database', 'test'])
		self.assertEqual(args.command, 'database')
		self.assertEqual(args.db_command, 'test')
		
		args = parser.parse_args(['database', 'execute', 'SELECT * FROM test'])
		self.assertEqual(args.db_command, 'execute')
		self.assertEqual(args.query, 'SELECT * FROM test')
		
		args = parser.parse_args(['database', 'info', 'my_table'])
		self.assertEqual(args.db_command, 'info')
		self.assertEqual(args.table_name, 'my_table')
	
	def test_parser_database_execute_with_params(self):
		"""
		Test database execute command with parameters.
		"""
		parser = create_parser()
		args = parser.parse_args(['database', 'execute', 'SELECT * FROM test WHERE id = ?', '--params', '["1"]'])
		self.assertEqual(args.params, '["1"]')
	
	def test_parser_messaging_subcommands(self):
		"""
		Test that parser has messaging subcommands.
		"""
		parser = create_parser()
		
		args = parser.parse_args(['messaging', 'test'])
		self.assertEqual(args.command, 'messaging')
		self.assertEqual(args.mq_command, 'test')
		
		args = parser.parse_args(['messaging', 'get', 'TEST.QUEUE'])
		self.assertEqual(args.mq_command, 'get')
		self.assertEqual(args.queue_name, 'TEST.QUEUE')
		
		args = parser.parse_args(['messaging', 'put', 'TEST.QUEUE', 'message'])
		self.assertEqual(args.mq_command, 'put')
		self.assertEqual(args.message, 'message')
		
		args = parser.parse_args(['messaging', 'depth', 'TEST.QUEUE'])
		self.assertEqual(args.mq_command, 'depth')
	
	def test_parser_messaging_get_with_timeout(self):
		"""
		Test messaging get command with timeout.
		"""
		parser = create_parser()
		args = parser.parse_args(['messaging', 'get', 'TEST.QUEUE', '--timeout', '30'])
		self.assertEqual(args.timeout, 30)
	
	def test_parser_messaging_put_with_properties(self):
		"""
		Test messaging put command with properties.
		"""
		parser = create_parser()
		args = parser.parse_args(['messaging', 'put', 'TEST.QUEUE', 'msg', '--properties', '{"priority": 5}'])
		self.assertEqual(args.properties, '{"priority": 5}')
	
	def test_parser_config_subcommands(self):
		"""
		Test that parser has config subcommands.
		"""
		parser = create_parser()
		
		args = parser.parse_args(['config', 'show'])
		self.assertEqual(args.command, 'config')
		self.assertEqual(args.config_command, 'show')
		
		args = parser.parse_args(['config', 'get', 'test.key'])
		self.assertEqual(args.config_command, 'get')
		self.assertEqual(args.key, 'test.key')
		
		args = parser.parse_args(['config', 'set', 'test.key', 'value'])
		self.assertEqual(args.config_command, 'set')
		self.assertEqual(args.key, 'test.key')
		self.assertEqual(args.value, 'value')
	
	def test_parser_test_all_command(self):
		"""
		Test that parser has test-all command.
		"""
		parser = create_parser()
		args = parser.parse_args(['test-all'])
		self.assertEqual(args.command, 'test-all')


class TestMain(unittest.TestCase):
	"""
	Test cases for main function.
	"""
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'test-all'])
	def test_main_test_all(self, mock_cli_class):
		"""
		Test main function with test-all command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.test_all.assert_called_once()
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'database', 'test'])
	def test_main_database_test(self, mock_cli_class):
		"""
		Test main function with database test command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.test_database.assert_called_once()
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'database', 'execute', 'SELECT * FROM test'])
	def test_main_database_execute(self, mock_cli_class):
		"""
		Test main function with database execute command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.execute_query.assert_called_once()
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'database', 'info', 'test_table'])
	def test_main_database_info(self, mock_cli_class):
		"""
		Test main function with database info command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.get_table_info.assert_called_once_with('test_table')
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'messaging', 'test'])
	def test_main_messaging_test(self, mock_cli_class):
		"""
		Test main function with messaging test command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.test_messaging.assert_called_once()
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'messaging', 'get', 'TEST.QUEUE'])
	def test_main_messaging_get(self, mock_cli_class):
		"""
		Test main function with messaging get command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.get_message.assert_called_once()
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'messaging', 'put', 'TEST.QUEUE', 'message'])
	def test_main_messaging_put(self, mock_cli_class):
		"""
		Test main function with messaging put command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.put_message.assert_called_once()
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'messaging', 'depth', 'TEST.QUEUE'])
	def test_main_messaging_depth(self, mock_cli_class):
		"""
		Test main function with messaging depth command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.get_queue_depth.assert_called_once_with('TEST.QUEUE')
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'config', 'show'])
	def test_main_config_show(self, mock_cli_class):
		"""
		Test main function with config show command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.show_config.assert_called_once()
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'config', 'get', 'test.key'])
	def test_main_config_get(self, mock_cli_class):
		"""
		Test main function with config get command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.get_config.assert_called_once_with('test.key')
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'config', 'set', 'test.key', 'value'])
	def test_main_config_set(self, mock_cli_class):
		"""
		Test main function with config set command.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli.set_config.assert_called_once_with('test.key', 'value')
	
	@patch('sys.argv', ['cli'])
	@patch('builtins.print')
	def test_main_no_command(self, mock_print):
		"""
		Test main function with no command (should print help).
		"""
		with patch('commonpython.cli.cli.create_parser') as mock_parser:
			parser_instance = MagicMock()
			parser_instance.parse_args.return_value = MagicMock(command=None, config=None)
			mock_parser.return_value = parser_instance
			
			main()
			
			parser_instance.print_help.assert_called_once()

	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'test-all'])
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'test-all'])
	@patch('sys.exit')
	def test_main_keyboard_interrupt(self, mock_exit, mock_argv, mock_cli_class):
		"""
		Test main function handles KeyboardInterrupt.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		mock_cli.test_all.side_effect = KeyboardInterrupt()
		
		with patch('builtins.print') as mock_print:
			main()
			
			mock_print.assert_called_with("\nOperation cancelled by user")
			mock_exit.assert_called_with(1)
	
	@patch('sys.exit')
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', 'test-all'])
	def test_main_exception(self, mock_cli_class, mock_exit):
		"""
		Test main function handles general exception.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		mock_cli.test_all.side_effect = Exception("Test error")
		
		with patch('builtins.print') as mock_print:
			main()
			
			mock_print.assert_called_with("Error: Test error")
			mock_exit.assert_called_with(1)
	
	@patch('commonpython.cli.cli.CLI')
	@patch('sys.argv', ['cli', '--config', 'test.yaml', 'test-all'])
	def test_main_with_config_file(self, mock_cli_class):
		"""
		Test main function with config file option.
		"""
		mock_cli = MagicMock()
		mock_cli_class.return_value = mock_cli
		
		main()
		
		mock_cli_class.assert_called_once_with('test.yaml')


if __name__ == '__main__':
	unittest.main()
