"""
Test cases for CLI

Tests command-line interface functionality using only standard Python modules.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path
import argparse

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.cli.cli import CLI, create_parser


class TestCLI(unittest.TestCase):
	"""
	Test cases for CLI class.
	
	@brief Comprehensive test suite for command-line interface functionality.
	"""

	@patch('sys.exit')
	def test_execute_query_setup_fail(self, mock_exit):
		"""
		@brief Test execute_query exits if setup fails.
		"""
		self.cli._setup_database = MagicMock(return_value=False)
		self.cli.execute_query('SELECT * FROM test')
		self.assertGreaterEqual(mock_exit.call_count, 1)
		mock_exit.assert_any_call(1)

	@patch('sys.exit')
	def test_execute_query_exception(self, mock_exit):
		"""
		Test execute_query exits on exception.
		"""
		self.cli._setup_database = MagicMock(return_value=True)
		self.cli.db_manager.execute_query = MagicMock(side_effect=Exception('fail'))
		self.cli.execute_query('SELECT * FROM test')
		mock_exit.assert_called_once_with(1)

	@patch('sys.exit')
	def test_get_table_info_setup_fail(self, mock_exit):
		"""
		@brief Test get_table_info exits if setup fails.
		"""
		self.cli._setup_database = MagicMock(return_value=False)
		self.cli.get_table_info('table')
		self.assertGreaterEqual(mock_exit.call_count, 1)
		mock_exit.assert_any_call(1)

	@patch('sys.exit')
	def test_get_table_info_exception(self, mock_exit):
		"""
		Test get_table_info exits on exception.
		"""
		self.cli._setup_database = MagicMock(return_value=True)
		self.cli.db_manager.get_table_info = MagicMock(side_effect=Exception('fail'))
		self.cli.get_table_info('table')
		mock_exit.assert_called_once_with(1)

	@patch('sys.exit')
	def test_put_message_setup_fail(self, mock_exit):
		"""
		@brief Test put_message exits if setup fails.
		"""
		self.cli._setup_messaging = MagicMock(return_value=False)
		self.cli.put_message('Q', 'msg')
		self.assertGreaterEqual(mock_exit.call_count, 1)
		mock_exit.assert_any_call(1)

	@patch('sys.exit')
	def test_put_message_exception(self, mock_exit):
		"""
		Test put_message exits on exception.
		"""
		self.cli._setup_messaging = MagicMock(return_value=True)
		self.cli.mq_manager.put_message = MagicMock(side_effect=Exception('fail'))
		self.cli.put_message('Q', 'msg')
		mock_exit.assert_called_once_with(1)

	@patch('sys.exit')
	def test_get_message_setup_fail(self, mock_exit):
		"""
		@brief Test get_message exits if setup fails.
		"""
		self.cli._setup_messaging = MagicMock(return_value=False)
		self.cli.get_message('Q')
		self.assertGreaterEqual(mock_exit.call_count, 1)
		mock_exit.assert_any_call(1)

	@patch('sys.exit')
	def test_get_message_exception(self, mock_exit):
		"""
		Test get_message exits on exception.
		"""
		self.cli._setup_messaging = MagicMock(return_value=True)
		self.cli.mq_manager.get_message = MagicMock(side_effect=Exception('fail'))
		self.cli.get_message('Q')
		mock_exit.assert_called_once_with(1)

	@patch('sys.exit')
	def test_get_queue_depth_setup_fail(self, mock_exit):
		"""
		@brief Test get_queue_depth exits if setup fails.
		"""
		self.cli._setup_messaging = MagicMock(return_value=False)
		self.cli.get_queue_depth('Q')
		self.assertGreaterEqual(mock_exit.call_count, 1)
		mock_exit.assert_any_call(1)

	@patch('sys.exit')
	def test_get_queue_depth_exception(self, mock_exit):
		"""
		Test get_queue_depth exits on exception.
		"""
		self.cli._setup_messaging = MagicMock(return_value=True)
		self.cli.mq_manager.get_queue_depth = MagicMock(side_effect=Exception('fail'))
		self.cli.get_queue_depth('Q')
		mock_exit.assert_called_once_with(1)
	
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
		with patch.object(self.cli, 'db_manager') as mock_db:
			with patch.object(self.cli, 'mq_manager') as mock_mq:
				self.cli.db_manager = mock_db
				self.cli.mq_manager = mock_mq
	
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
			config_file = f.name
		
		try:
			cli = CLI(config_file)
			self.assertEqual(cli.config_file, config_file)
		finally:
			os.unlink(config_file)
	
		def test_db_command_error(self):
			"""
			Test error branch for db command.
			"""
			self.cli.db_manager.connect = MagicMock(side_effect=Exception("fail"))
			with self.assertRaises(Exception):
				self.cli.db_command('test')

		def test_mq_command_error(self):
			"""
			Test error branch for mq command.
			"""
			self.cli.mq_manager.connect = MagicMock(side_effect=Exception("fail"))
			with self.assertRaises(Exception):
				self.cli.mq_command('test')

		def test_config_command_error(self):
			"""
			Test error branch for config command.
			"""
			self.cli.config_manager.get = MagicMock(side_effect=Exception("fail"))
			with self.assertRaises(Exception):
				self.cli.config_command('show')
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
		self.cli = CLI(self.config_file)
		self.cli.db_manager = mock_db_manager
		mock_db_manager.connect.return_value = True
		result = self.cli._setup_database()
		self.assertTrue(result)
		self.assertIs(self.cli.db_manager, mock_db_manager)
	
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
		self.cli = CLI(self.config_file)
		self.cli.db_manager = mock_db_manager
		mock_db_manager.connect.side_effect = Exception("fail")
		with patch('builtins.print') as mock_print:
			result = self.cli._setup_database()
			self.assertFalse(result)
			mock_print.assert_called()
	
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
		self.cli = CLI(self.config_file)
		self.cli.mq_manager = mock_mq_manager
		mock_mq_manager.connect.return_value = True
		result = self.cli._setup_messaging()
		self.assertTrue(result)
		self.assertIs(self.cli.mq_manager, mock_mq_manager)
	
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
		self.cli = CLI(self.config_file)
		self.cli.mq_manager = mock_mq_manager
		mock_mq_manager.connect.side_effect = Exception("fail")
		with patch('builtins.print') as mock_print:
			result = self.cli._setup_messaging()
			self.assertFalse(result)
			mock_print.assert_called()
	
	def test_display_results_empty(self):
		"""
		Test displaying empty results.
		
		@brief Test that empty results are displayed correctly.
		"""
		with patch('builtins.print') as mock_print:
			self.cli._display_results([], "Test Results")
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
			self.assertTrue(mock_print.call_count >= 3)
	
	def test_display_results_other(self):
		"""
		Test displaying other types of results.
		
		@brief Test that other result types are displayed as JSON.
		"""
		results = {'key': 'value', 'number': 123}
		
		with patch('builtins.print') as mock_print:
			self.cli._display_results(results, "Test Results")
			
			# Should print JSON representation
			mock_print.assert_called()
	
	@patch.object(CLI, '_setup_database')
	def test_test_database_success(self, mock_setup):
		"""
		Test successful database testing.
		
		@brief Test that database testing succeeds.
		"""
		mock_setup.return_value = True
		self.cli.db_manager = MagicMock()
		self.cli.db_manager.test_connection.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.test_database()
			
			mock_print.assert_called_with("✓ Database connection successful")
	
	@patch.object(CLI, '_setup_database')
	def test_test_database_failure(self, mock_setup):
		"""
		Test failed database testing.
		
		@brief Test that database testing failures are handled correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager = MagicMock()
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
		self.cli.db_manager = MagicMock()
		self.cli.db_manager.execute_query.return_value = [{'id': 1, 'name': 'test'}]
		
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.execute_query("SELECT * FROM test")
			
			self.cli.db_manager.execute_query.assert_called_once_with("SELECT * FROM test", None)
			mock_display.assert_called_once()
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_update(self, mock_setup):
		"""
		Test executing UPDATE query.
		
		@brief Test that UPDATE queries are executed correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager = MagicMock()
		self.cli.db_manager.execute_update.return_value = 1
		
		with patch('builtins.print') as mock_print:
			self.cli.execute_query("UPDATE test SET col = 1")
			
			self.cli.db_manager.execute_update.assert_called_once_with("UPDATE test SET col = 1", None)
			mock_print.assert_called_with("Query executed successfully. Rows affected: 1")
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_setup_failure(self, mock_setup):
		"""
		Test query execution with setup failure.
		
		@brief Test that query execution handles setup failures correctly.
		"""
		mock_setup.return_value = False
		
		with self.assertRaises(SystemExit):
			self.cli.execute_query("SELECT * FROM test")
	
	@patch.object(CLI, '_setup_database')
	def test_execute_query_with_params(self, mock_setup):
		"""
		Test executing query with parameters.
		
		@brief Test that queries with parameters are executed correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager = MagicMock()
		self.cli.db_manager.execute_query.return_value = [{'id': 1}]
		
		with patch.object(self.cli, '_display_results'):
			self.cli.execute_query("SELECT * FROM test WHERE id = ?", '["1"]')
			
			self.cli.db_manager.execute_query.assert_called_once_with("SELECT * FROM test WHERE id = ?", ("1",))
	
	@patch.object(CLI, '_setup_database')
	def test_get_table_info(self, mock_setup):
		"""
		Test getting table information.
		
		@brief Test that table information is retrieved correctly.
		"""
		mock_setup.return_value = True
		self.cli.db_manager = MagicMock()
		self.cli.db_manager.get_table_info.return_value = [{'COLNAME': 'id', 'TYPENAME': 'INTEGER'}]
		
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.get_table_info("test_table")
			
			self.cli.db_manager.get_table_info.assert_called_once_with("test_table")
			mock_display.assert_called_once()
	
	@patch.object(CLI, '_setup_messaging')
	def test_test_messaging_success(self, mock_setup):
		"""
		Test successful messaging testing.
		
		@brief Test that messaging testing succeeds.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager = MagicMock()
		self.cli.mq_manager.test_connection.return_value = True
		
		with patch('builtins.print') as mock_print:
			self.cli.test_messaging()
			
			mock_print.assert_called_with("✓ MQ connection successful")
	
	@patch.object(CLI, '_setup_messaging')
	def test_get_message_success(self, mock_setup):
		"""
		Test successful message retrieval.
		
		@brief Test that messages are retrieved successfully.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager = MagicMock()
		self.cli.mq_manager.get_message.return_value = {'data': 'test message'}
		
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.get_message("TEST.QUEUE")
			
			self.cli.mq_manager.get_message.assert_called_once_with("TEST.QUEUE", None)
			mock_display.assert_called_once()
	
	@patch.object(CLI, '_setup_messaging')
	def test_get_message_no_message(self, mock_setup):
		"""
		Test message retrieval when no message available.
		
		@brief Test that no message case is handled correctly.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager = MagicMock()
		self.cli.mq_manager.get_message.return_value = None
		mock_setup.return_value = True
		self.cli.mq_manager.get_message.return_value = None
		with patch('builtins.print') as mock_print:
			self.cli.get_message("TEST.QUEUE")
			
			mock_print.assert_called_with("No message available in queue TEST.QUEUE")
	
	@patch.object(CLI, '_setup_messaging')
	def test_put_message_success(self, mock_setup):
		"""
		Test successful message sending.
		
		@brief Test that messages are sent successfully.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager = MagicMock()
		self.cli.mq_manager.put_message.return_value = True
		mock_setup.return_value = True
		with patch('builtins.print') as mock_print:
			self.cli.put_message("TEST.QUEUE", "test message")
			
			self.cli.mq_manager.put_message.assert_called_once()
			mock_print.assert_called_with("Message sent to queue TEST.QUEUE")
	
	@patch.object(CLI, '_setup_messaging')
	def test_put_message_failure(self, mock_setup):
		"""
		Test failed message sending.
		
		@brief Test that message sending failures are handled correctly.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager = MagicMock()
		self.cli.mq_manager.put_message.return_value = False
		mock_setup.return_value = True
		with self.assertRaises(SystemExit):
			self.cli.put_message("TEST.QUEUE", "test message")
	
	@patch.object(CLI, '_setup_messaging')
	def test_get_queue_depth(self, mock_setup):
		"""
		Test getting queue depth.
		
		@brief Test that queue depth is retrieved correctly.
		"""
		mock_setup.return_value = True
		self.cli.mq_manager = MagicMock()
		self.cli.mq_manager.get_queue_depth.return_value = 5
		mock_setup.return_value = True
		with patch('builtins.print') as mock_print:
			self.cli.get_queue_depth("TEST.QUEUE")
			
			self.cli.mq_manager.get_queue_depth.assert_called_once_with("TEST.QUEUE")
			mock_print.assert_called_with("Queue TEST.QUEUE depth: 5")
	
	def test_show_config(self):
		"""
		Test showing configuration.
		
		@brief Test that configuration is displayed correctly.
		"""
		with patch.object(self.cli, '_display_results') as mock_display:
			self.cli.show_config()
			
			mock_display.assert_called_once()
	
	def test_get_config(self):
		"""
		Test getting configuration value.
		
		@brief Test that configuration values are retrieved correctly.
		"""
		with patch.object(self.cli.config_manager, 'get') as mock_get:
			mock_get.return_value = 'test_value'
			
			with patch('builtins.print') as mock_print:
				self.cli.get_config('test.key')
				
				mock_get.assert_called_once_with('test.key')
				mock_print.assert_called_with("test.key: test_value")
	
	def test_set_config(self):
		"""
		Test setting configuration value.
		
		@brief Test that configuration values are set correctly.
		"""
		with patch.object(self.cli.config_manager, 'set') as mock_set:
			with patch('builtins.print') as mock_print:
				self.cli.set_config('test.key', 'test_value')
				
				mock_set.assert_called_once_with('test.key', 'test_value')
				mock_print.assert_called_with("Set test.key = test_value")
	
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
	def test_parser_has_subcommands(self):
		"""
		Test that parser has subcommands.
        
		@brief Test that parser includes all expected subcommands.
		"""
		parser = create_parser()
		args = parser.parse_args(['database', 'test'])
		self.assertEqual(args.command, 'database')
		self.assertEqual(args.db_command, 'test')
		args = parser.parse_args(['messaging', 'test'])
		self.assertEqual(args.command, 'messaging')
		self.assertEqual(args.mq_command, 'test')
		args = parser.parse_args(['config', 'show'])
		self.assertEqual(args.command, 'config')
		self.assertEqual(args.config_command, 'show')
		args = parser.parse_args(['test-all'])
		self.assertEqual(args.command, 'test-all')
