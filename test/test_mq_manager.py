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
    
    def test_disconnect(self):
        """
        Test MQ disconnection.
        
        @brief Test that MQ disconnection works correctly.
        """
        self.mq_manager.connected = True
        self.mq_manager.disconnect()
        self.assertFalse(self.mq_manager.connected)
    
    def test_is_connected(self):
        """
        Test connection status check.
        
        @brief Test that connection status is checked correctly.
        """
        self.assertFalse(self.mq_manager.is_connected())
        
        self.mq_manager.connected = True
        self.assertTrue(self.mq_manager.is_connected())
    
    @patch('subprocess.run')
    def test_put_message_success(self, mock_run):
        """
        Test successful message sending.
        
        @brief Test that messages are sent successfully.
        """
        self.mq_manager.connected = True
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Message sent"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.mq_manager.put_message("TEST.QUEUE", "test message")
        
        self.assertTrue(result)
    
    @patch('subprocess.run')
    def test_put_message_failure(self, mock_run):
        """
        Test failed message sending.
        
        @brief Test that message sending failures are handled correctly.
        """
        self.mq_manager.connected = True
        
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
    
    def test_put_message_dict(self):
        """
        Test sending dictionary message.
        
        @brief Test that dictionary messages are converted to JSON.
        """
        self.mq_manager.connected = True
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Message sent"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            message_dict = {"key": "value", "number": 123}
            result = self.mq_manager.put_message("TEST.QUEUE", message_dict)
            
            self.assertTrue(result)
    
    def test_put_message_bytes(self):
        """
        Test sending bytes message.
        
        @brief Test that bytes messages are handled correctly.
        """
        self.mq_manager.connected = True
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Message sent"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            message_bytes = b"binary message"
            result = self.mq_manager.put_message("TEST.QUEUE", message_bytes)
            
            self.assertTrue(result)
    
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
    
    def test_get_message_not_connected(self):
        """
        Test message retrieval when not connected.
        
        @brief Test that message retrieval fails when not connected to MQ.
        """
        with self.assertRaises(Exception) as context:
            self.mq_manager.get_message("TEST.QUEUE")
        
        self.assertIn("connection not established", str(context.exception))
    
    @patch('subprocess.run')
    def test_browse_message_success(self, mock_run):
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
    
    def test_browse_message_not_connected(self):
        """
        Test message browsing when not connected.
        
        @brief Test that message browsing fails when not connected to MQ.
        """
        with self.assertRaises(Exception) as context:
            self.mq_manager.browse_message("TEST.QUEUE")
        
        self.assertIn("connection not established", str(context.exception))
    
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
    
    @patch('subprocess.run')
    def test_get_message_json_decode_error(self, mock_run):
        """
        @brief Test get_message with invalid JSON (should fallback to string).
        """
        self.mq_manager.connected = True
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{invalid_json}'
            mock_result.stderr = ''
            mock_run.return_value = mock_result
            result = self.mq_manager.get_message('TEST.QUEUE')
            self.assertIsInstance(result['data'], str)
    
    def test_get_queue_depth_parse_error(self):
        """
        @brief Test get_queue_depth with unparsable CURDEPTH value.
        """
        self.mq_manager.connected = True
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = 'CURDEPTH notanumber'
            mock_result.stderr = ''
            mock_run.return_value = mock_result
            result = self.mq_manager.get_queue_depth('TEST.QUEUE')
            self.assertEqual(result, 0)
    
    @patch('subprocess.run')
    def test_execute_mq_command_logger_error(self, mock_run):
        """
        @brief Test _execute_mq_command with logger raising error.
        """
        mq_manager = MQManager(self.config, MagicMock())
        mq_manager.logger.logger.error.side_effect = Exception("Logger fail")
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
    def test_get_queue_depth_unexpected_output(self, mock_run):
        """
        @brief Test get_queue_depth with unexpected CLI output.
        """
        self.mq_manager.connected = True
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = 'SOMETHING ELSE'
            mock_result.stderr = ''
            mock_run.return_value = mock_result
            result = self.mq_manager.get_queue_depth('TEST.QUEUE')
            self.assertEqual(result, 0)

