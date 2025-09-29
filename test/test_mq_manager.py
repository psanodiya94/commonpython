"""
Test cases for MQManager

Tests messaging functionality using CLI interface with mocked subprocess calls.
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
import sys
from pathlib import Path

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.messaging.mq_manager import MQManager


class TestMQManager(unittest.TestCase):
    """
    Test cases for MQManager class.
    
    @brief Comprehensive test suite for messaging functionality using CLI interface.
    """
    
    def setUp(self):
        """
        Set up test fixtures.
        
        @brief Initialize test environment before each test.
        """
        self.config = {
            'host': 'localhost',
            'port': 1414,
            'queue_manager': 'TEST_QM',
            'channel': 'TEST.CHANNEL',
            'user': 'testuser',
            'password': 'testpass',
            'timeout': 30
        }
        self.mq_manager = MQManager(self.config)
    
    def test_init(self):
        """
        Test MQManager initialization.
        
        @brief Test that MQManager initializes correctly with configuration.
        """
        self.assertEqual(self.mq_manager.config, self.config)
        self.assertIsNone(self.mq_manager.logger)
        self.assertFalse(self.mq_manager.connected)
    
    def test_init_with_logger(self):
        """
        Test MQManager initialization with logger.
        
        @brief Test MQManager initialization with logger instance.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        self.assertEqual(mq_manager.logger, mock_logger)
    
    def test_init_empty_config(self):
        """
        Test MQManager initialization with empty config.
        """
        mq_manager = MQManager({})
        self.assertIsNotNone(mq_manager.connection_info)
        self.assertEqual(mq_manager.connection_info['host'], 'localhost')
    
    def test_build_connection_info(self):
        """
        Test building connection information.
        
        @brief Test that connection information is built correctly from configuration.
        """
        conn_info = self.mq_manager._build_connection_info()
        
        expected = {
            'host': 'localhost',
            'port': 1414,
            'queue_manager': 'TEST_QM',
            'channel': 'TEST.CHANNEL',
            'user': 'testuser',
            'password': 'testpass',
            'timeout': 30
        }
        
        self.assertEqual(conn_info, expected)
    
    def test_build_connection_info_minimal(self):
        """
        Test building connection information with minimal configuration.
        
        @brief Test connection information building with minimal configuration.
        """
        minimal_config = {'queue_manager': 'TEST_QM'}
        mq_manager = MQManager(minimal_config)
        conn_info = mq_manager._build_connection_info()
        
        self.assertEqual(conn_info['host'], 'localhost')
        self.assertEqual(conn_info['port'], 1414)
        self.assertEqual(conn_info['queue_manager'], 'TEST_QM')
        self.assertEqual(conn_info['channel'], 'SYSTEM.DEF.SVRCONN')
    
    def test_build_connection_info_with_defaults(self):
        """
        Test that build_connection_info applies correct defaults.
        """
        config = {'queue_manager': 'QM1'}
        mq_manager = MQManager(config)
        conn_info = mq_manager._build_connection_info()
        
        self.assertEqual(conn_info['user'], '')
        self.assertEqual(conn_info['password'], '')
        self.assertEqual(conn_info['timeout'], 30)
    
    @patch('subprocess.run')
    def test_execute_mq_command_success(self, mock_run):
        """
        Test successful MQ command execution.
        
        @brief Test that MQ commands execute successfully.
        """
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager._execute_mq_command("display", ["qmgr"])
        
        self.assertTrue(result['success'])
        self.assertEqual(result['stdout'], "Success")
        self.assertEqual(result['returncode'], 0)
    
    @patch('subprocess.run')
    def test_execute_mq_command_failure(self, mock_run):
        """
        Test failed MQ command execution.
        
        @brief Test that failed MQ commands are handled correctly.
        """
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_run.return_value = mock_result
        
        result = self.mq_manager._execute_mq_command("display", ["qmgr"])
        
        self.assertFalse(result['success'])
        self.assertEqual(result['stderr'], "Command failed")
        self.assertEqual(result['returncode'], 1)
    
    @patch('subprocess.run')
    def test_execute_mq_command_with_no_params(self, mock_run):
        """
        Test MQ command execution without parameters.
        """
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager._execute_mq_command("display")
        
        self.assertTrue(result['success'])
    
    @patch('subprocess.run')
    def test_execute_mq_command_timeout(self, mock_run):
        """
        Test MQ command timeout.
        
        @brief Test that command timeouts are handled correctly.
        """
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("runmqsc", 30)
        
        with self.assertRaises(Exception) as context:
            self.mq_manager._execute_mq_command("display", ["qmgr"])
        
        self.assertIn("timeout", str(context.exception))
    
    @patch('subprocess.run')
    def test_execute_mq_command_general_exception(self, mock_run):
        """
        Test MQ command general exception.
        """
        mock_run.side_effect = Exception("General error")
        
        with self.assertRaises(Exception) as context:
            self.mq_manager._execute_mq_command("display", ["qmgr"])
        
        self.assertIn("MQ command error", str(context.exception))
    
    @patch('subprocess.run')
    def test_execute_mq_command_logger_error(self, mock_run):
        """
        @brief Test _execute_mq_command with logger raising error.
        """
        mq_manager = MQManager(self.config, MagicMock())
        mq_manager.logger.logger.error = MagicMock(side_effect=Exception("Logger fail"))
        
        with patch('subprocess.run', side_effect=Exception("subprocess error")):
            with self.assertRaises(Exception):
                mq_manager._execute_mq_command("display", ["qmgr"])
    
    @patch('subprocess.run')
    def test_execute_mq_command_no_logger(self, mock_run):
        """
        @brief Test _execute_mq_command with no logger present.
        """
        mq_manager = MQManager(self.config)
        
        with patch('subprocess.run', side_effect=Exception("subprocess error")):
            with self.assertRaises(Exception):
                mq_manager._execute_mq_command("display", ["qmgr"])
    
    @patch('subprocess.run')
    def test_connect_success(self, mock_run):
        """
        Test successful MQ connection.
        
        @brief Test that MQ connection succeeds.
        """
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "QMGR display successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.connect()
        
        self.assertTrue(result)
        self.assertTrue(self.mq_manager.connected)
    
    @patch('subprocess.run')
    def test_connect_success_with_logger(self, mock_run):
        """
        Test successful connection with logger.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "QMGR display successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = mq_manager.connect()
        
        self.assertTrue(result)
        mock_logger.logger.info.assert_called()
    
    @patch('subprocess.run')
    def test_connect_failure(self, mock_run):
        """
        Test failed MQ connection.
        
        @brief Test that MQ connection failures are handled correctly.
        """
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Connection failed"
        mock_run.return_value = mock_result
        
        result = self.mq_manager.connect()
        
        self.assertFalse(result)
        self.assertFalse(self.mq_manager.connected)
    
    @patch('subprocess.run')
    def test_connect_failure_with_logger(self, mock_run):
        """
        Test failed connection with logger.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Connection failed"
        mock_run.return_value = mock_result
        
        result = mq_manager.connect()
        
        self.assertFalse(result)
        mock_logger.logger.error.assert_called()
    
    @patch('subprocess.run')
    def test_connect_exception(self, mock_run):
        """
        Test connection with exception.
        """
        mock_run.side_effect = Exception("Connection error")
        
        result = self.mq_manager.connect()
        
        self.assertFalse(result)
        self.assertFalse(self.mq_manager.connected)
    
    def test_disconnect(self):
        """
        Test MQ disconnection.
        
        @brief Test that MQ disconnection works correctly.
        """
        self.mq_manager.connected = True
        self.mq_manager.disconnect()
        self.assertFalse(self.mq_manager.connected)
    
    def test_disconnect_with_logger(self):
        """
        Test disconnection with logger.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        mq_manager.connected = True
        
        mq_manager.disconnect()
        
        self.assertFalse(mq_manager.connected)
        mock_logger.logger.info.assert_called()
    
    def test_disconnect_exception(self):
        """
        Test disconnect handles exception gracefully.
        """
        mock_logger = MagicMock()
        mock_logger.logger.info.side_effect = Exception("Logger error")
        mq_manager = MQManager(self.config, mock_logger)
        mq_manager.connected = True
        
        # Should not raise exception
        mq_manager.disconnect()
        self.assertFalse(mq_manager.connected)
    
    def test_is_connected(self):
        """
        Test connection status check.
        
        @brief Test that connection status is checked correctly.
        """
        self.assertFalse(self.mq_manager.is_connected())
        
        self.mq_manager.connected = True
        self.assertTrue(self.mq_manager.is_connected())
    
    @patch('subprocess.run')
    @patch('os.unlink')
    @patch('tempfile.NamedTemporaryFile')
    def test_put_message_success(self, mock_tempfile, mock_unlink, mock_run):
        """
        Test successful message sending.
        
        @brief Test that messages are sent successfully.
        """
        self.mq_manager.connected = True
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.msg'
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Message sent"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.put_message("TEST.QUEUE", "test message")
        
        self.assertTrue(result)
        mock_unlink.assert_called_once()
    
    @patch('subprocess.run')
    @patch('os.unlink')
    @patch('tempfile.NamedTemporaryFile')
    def test_put_message_failure(self, mock_tempfile, mock_unlink, mock_run):
        """
        Test failed message sending.
        
        @brief Test that message sending failures are handled correctly.
        """
        self.mq_manager.connected = True
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.msg'
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Send failed"
        mock_run.return_value = mock_result
        
        result = self.mq_manager.put_message("TEST.QUEUE", "test message")
        
        self.assertFalse(result)
    
    def test_put_message_not_connected(self):
        """
        Test message sending when not connected.
        
        @brief Test that message sending fails when not connected to MQ.
        """
        with self.assertRaises(Exception) as context:
            self.mq_manager.put_message("TEST.QUEUE", "test message")
        
        self.assertIn("connection not established", str(context.exception))
    
    @patch('subprocess.run')
    @patch('os.unlink')
    @patch('tempfile.NamedTemporaryFile')
    def test_put_message_dict(self, mock_tempfile, mock_unlink, mock_run):
        """
        Test sending dictionary message.
        
        @brief Test that dictionary messages are converted to JSON.
        """
        self.mq_manager.connected = True
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.msg'
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Message sent"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        message_dict = {"key": "value", "number": 123}
        result = self.mq_manager.put_message("TEST.QUEUE", message_dict)
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    @patch('os.unlink')
    @patch('tempfile.NamedTemporaryFile')
    def test_put_message_bytes(self, mock_tempfile, mock_unlink, mock_run):
        """
        Test sending bytes message.
        
        @brief Test that bytes messages are handled correctly.
        """
        self.mq_manager.connected = True
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.msg'
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Message sent"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        message_bytes = b"binary message"
        result = self.mq_manager.put_message("TEST.QUEUE", message_bytes)
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    @patch('os.unlink')
    @patch('tempfile.NamedTemporaryFile')
    def test_put_message_with_properties(self, mock_tempfile, mock_unlink, mock_run):
        """
        Test sending message with properties.
        """
        self.mq_manager.connected = True
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.msg'
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Message sent"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        properties = {"priority": 5}
        result = self.mq_manager.put_message("TEST.QUEUE", "test message", properties)
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    @patch('os.unlink')
    @patch('tempfile.NamedTemporaryFile')
    def test_put_message_with_logger(self, mock_tempfile, mock_unlink, mock_run):
        """
        Test put message with logger.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        mq_manager.connected = True
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.msg'
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Message sent"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = mq_manager.put_message("TEST.QUEUE", "test message")
        
        self.assertTrue(result)
        mock_logger.log_mq_operation.assert_called_once()
    
    @patch('subprocess.run')
    @patch('os.unlink')
    @patch('tempfile.NamedTemporaryFile')
    def test_put_message_exception(self, mock_tempfile, mock_unlink, mock_run):
        """
        Test put message with exception.
        """
        self.mq_manager.connected = True
        
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test.msg'
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_file
        
        mock_run.side_effect = Exception("Send error")
        
        result = self.mq_manager.put_message("TEST.QUEUE", "test message")
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_get_message_success(self, mock_run):
        """
        Test successful message retrieval.
        
        @brief Test that messages are retrieved successfully.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"message": "test data"}'
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_message("TEST.QUEUE")
        
        self.assertIsNotNone(result)
        self.assertIn('data', result)
        self.assertIn('properties', result)
        self.assertIn('raw_bytes', result)
    
    @patch('subprocess.run')
    def test_get_message_plain_text(self, mock_run):
        """
        Test getting plain text message.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'plain text message'
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_message("TEST.QUEUE")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['data'], 'plain text message')
    
    @patch('subprocess.run')
    def test_get_message_no_message(self, mock_run):
        """
        Test message retrieval when no message available.
        
        @brief Test that None is returned when no message is available.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_message("TEST.QUEUE")
        
        self.assertIsNone(result)
    
    @patch('subprocess.run')
    def test_get_message_with_timeout(self, mock_run):
        """
        Test message retrieval with custom timeout.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "test message"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_message("TEST.QUEUE", timeout=10)
        
        self.assertIsNotNone(result)
    
    def test_get_message_not_connected(self):
        """
        Test message retrieval when not connected.
        
        @brief Test that message retrieval fails when not connected to MQ.
        """
        with self.assertRaises(Exception) as context:
            self.mq_manager.get_message("TEST.QUEUE")
        
        self.assertIn("connection not established", str(context.exception))
    
    @patch('subprocess.run')
    def test_get_message_json_decode_error(self, mock_run):
        """
        @brief Test get_message with invalid JSON (should fallback to string).
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{invalid_json}'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_message('TEST.QUEUE')
        
        self.assertIsInstance(result['data'], str)
        self.assertEqual(result['data'], '{invalid_json}')
    
    @patch('subprocess.run')
    def test_get_message_with_logger(self, mock_run):
        """
        Test get message with logger.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "test message"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = mq_manager.get_message("TEST.QUEUE")
        
        self.assertIsNotNone(result)
        mock_logger.log_mq_operation.assert_called_once()
    
    @patch('subprocess.run')
    def test_get_message_exception(self, mock_run):
        """
        Test get message with exception.
        """
        self.mq_manager.connected = True
        
        mock_run.side_effect = Exception("Get error")
        
        with self.assertRaises(Exception):
            self.mq_manager.get_message("TEST.QUEUE")
    
    def test_browse_message_not_connected(self):
        """
        Test message browsing when not connected.
        
        @brief Test that message browsing fails when not connected to MQ.
        """
        with self.assertRaises(Exception) as context:
            self.mq_manager.browse_message("TEST.QUEUE")
        
        self.assertIn("connection not established", str(context.exception))
    
    def test_browse_message_success(self):
        """
        Test successful message browsing.
        
        @brief Test that messages are browsed successfully.
        """
        self.mq_manager.connected = True
        
        # Mock get_message to return a message
        with patch.object(self.mq_manager, 'get_message') as mock_get:
            mock_get.return_value = {
                'data': 'test message',
                'properties': {'message_id': 'msg123'},
                'raw_bytes': b'test message'
            }
            
            # Mock put_message to succeed
            with patch.object(self.mq_manager, 'put_message') as mock_put:
                mock_put.return_value = True
                
                result = self.mq_manager.browse_message("TEST.QUEUE")
                
                self.assertIsNotNone(result)
                self.assertEqual(result['data'], 'test message')
                mock_get.assert_called_once()
                mock_put.assert_called_once()
    
    def test_browse_message_no_message(self):
        """
        Test browsing when no message available.
        """
        self.mq_manager.connected = True
        
        with patch.object(self.mq_manager, 'get_message') as mock_get:
            mock_get.return_value = None
            
            result = self.mq_manager.browse_message("TEST.QUEUE")
            
            self.assertIsNone(result)
    
    def test_browse_message_with_logger(self):
        """
        Test browse message with logger.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        mq_manager.connected = True
        
        with patch.object(mq_manager, 'get_message') as mock_get:
            mock_get.return_value = {
                'data': 'test message',
                'properties': {'message_id': 'msg123'},
                'raw_bytes': b'test message'
            }
            
            with patch.object(mq_manager, 'put_message') as mock_put:
                mock_put.return_value = True
                
                result = mq_manager.browse_message("TEST.QUEUE")
                
                self.assertIsNotNone(result)
                mock_logger.log_mq_operation.assert_called()
    
    def test_browse_message_exception(self):
        """
        Test browse message with exception.
        """
        self.mq_manager.connected = True
        
        with patch.object(self.mq_manager, 'get_message') as mock_get:
            mock_get.side_effect = Exception("Browse error")
            
            with self.assertRaises(Exception):
                self.mq_manager.browse_message("TEST.QUEUE")
    
    @patch('subprocess.run')
    def test_get_queue_depth_success(self, mock_run):
        """
        Test successful queue depth retrieval.
        
        @brief Test that queue depth is retrieved successfully.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "CURDEPTH 5"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_queue_depth("TEST.QUEUE")
        
        self.assertEqual(result, 5)
    
    @patch('subprocess.run')
    def test_get_queue_depth_zero(self, mock_run):
        """
        Test queue depth of zero.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "CURDEPTH 0"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_queue_depth("TEST.QUEUE")
        
        self.assertEqual(result, 0)
    
    @patch('subprocess.run')
    def test_get_queue_depth_failure(self, mock_run):
        """
        Test failed queue depth retrieval.
        
        @brief Test that queue depth retrieval failures are handled correctly.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Queue not found"
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_queue_depth("TEST.QUEUE")
        
        self.assertEqual(result, -1)
    
    def test_get_queue_depth_not_connected(self):
        """
        Test queue depth retrieval when not connected.
        
        @brief Test that queue depth retrieval fails when not connected to MQ.
        """
        with self.assertRaises(Exception) as context:
            self.mq_manager.get_queue_depth("TEST.QUEUE")
        
        self.assertIn("connection not established", str(context.exception))
    
    def test_get_queue_depth_parse_error(self):
        """
        @brief Test get_queue_depth with unparsable CURDEPTH value.
        """
        self.mq_manager.connected = True
        
        with patch.object(self.mq_manager, '_execute_mq_command') as mock_exec:
            mock_exec.return_value = {
                'success': True,
                'stdout': 'CURDEPTH notanumber',
                'stderr': '',
                'returncode': 0
            }
            
            result = self.mq_manager.get_queue_depth('TEST.QUEUE')
            self.assertEqual(result, 0)
    
    @patch('subprocess.run')
    def test_get_queue_depth_unexpected_output(self, mock_run):
        """
        @brief Test get_queue_depth with unexpected CLI output.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'SOMETHING ELSE'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = self.mq_manager.get_queue_depth('TEST.QUEUE')
        self.assertEqual(result, 0)
    
    @patch('subprocess.run')
    def test_get_queue_depth_exception(self, mock_run):
        """
        Test get queue depth with exception.
        """
        self.mq_manager.connected = True
        
        mock_run.side_effect = Exception("Depth error")
        
        result = self.mq_manager.get_queue_depth("TEST.QUEUE")
        
        self.assertEqual(result, -1)
    
    @patch('subprocess.run')
    def test_purge_queue_success(self, mock_run):
        """
        Test successful queue purging.
        
        @brief Test that queues are purged successfully.
        """
        self.mq_manager.connected = True
        
        # Mock get_queue_depth to return initial depth
        with patch.object(self.mq_manager, 'get_queue_depth') as mock_depth:
            mock_depth.return_value = 5
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Queue cleared"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            result = self.mq_manager.purge_queue("TEST.QUEUE")
            
            self.assertEqual(result, 5)
    
    @patch('subprocess.run')
    def test_purge_queue_empty(self, mock_run):
        """
        Test purging empty queue.
        """
        self.mq_manager.connected = True
        
        with patch.object(self.mq_manager, 'get_queue_depth') as mock_depth:
            mock_depth.return_value = 0
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Queue cleared"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            result = self.mq_manager.purge_queue("TEST.QUEUE")
            
            self.assertEqual(result, 0)
    
    @patch('subprocess.run')
    def test_purge_queue_failure(self, mock_run):
        """
        Test failed queue purging.
        
        @brief Test that queue purging failures are handled correctly.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Purge failed"
        mock_run.return_value = mock_result
        
        with self.assertRaises(Exception) as context:
            self.mq_manager.purge_queue("TEST.QUEUE")
        
        self.assertIn("Failed to purge queue", str(context.exception))
    
    def test_purge_queue_not_connected(self):
        """
        Test queue purging when not connected.
        
        @brief Test that queue purging fails when not connected to MQ.
        """
        with self.assertRaises(Exception) as context:
            self.mq_manager.purge_queue("TEST.QUEUE")
        
        self.assertIn("connection not established", str(context.exception))
    
    def test_purge_queue_with_logger(self):
        """
        Test purge queue with logger.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        mq_manager.connected = True
        
        with patch.object(mq_manager, 'get_queue_depth') as mock_depth:
            mock_depth.return_value = 5
            
            with patch.object(mq_manager, '_execute_mq_command') as mock_exec:
                mock_exec.return_value = {
                    'success': True,
                    'stdout': 'Queue cleared',
                    'stderr': '',
                    'returncode': 0
                }
                
                result = mq_manager.purge_queue("TEST.QUEUE")
                
                self.assertEqual(result, 5)
                mock_logger.log_mq_operation.assert_called()
    
    def test_purge_queue_exception(self):
        """
        Test purge queue with exception.
        """
        self.mq_manager.connected = True
        
        with patch.object(self.mq_manager, 'get_queue_depth') as mock_depth:
            mock_depth.return_value = 5
            
            with patch.object(self.mq_manager, '_execute_mq_command') as mock_exec:
                mock_exec.side_effect = Exception("Purge error")
                
                with self.assertRaises(Exception):
                    self.mq_manager.purge_queue("TEST.QUEUE")
    
    @patch('subprocess.run')
    def test_test_connection_success(self, mock_run):
        """
        Test successful connection test.
        
        @brief Test that connection testing works correctly.
        """
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "QMGR display successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.test_connection()
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_test_connection_failure(self, mock_run):
        """
        Test failed connection test.
        
        @brief Test that connection testing failures are handled correctly.
        """
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Connection failed"
        mock_run.return_value = mock_result
        
        result = self.mq_manager.test_connection()
        
        self.assertFalse(result)
    
    def test_test_connection_exception(self):
        """
        Test connection test with exception.
        """
        with patch.object(self.mq_manager, '_execute_mq_command') as mock_exec:
            mock_exec.side_effect = Exception("Test error")
            
            result = self.mq_manager.test_connection()
            
            self.assertFalse(result)
    
    def test_test_connection_with_logger(self):
        """
        Test connection test with logger and exception.
        """
        mock_logger = MagicMock()
        mq_manager = MQManager(self.config, mock_logger)
        
        with patch.object(mq_manager, '_execute_mq_command') as mock_exec:
            mock_exec.side_effect = Exception("Test error")
            
            result = mq_manager.test_connection()
            
            self.assertFalse(result)
            mock_logger.logger.error.assert_called()
