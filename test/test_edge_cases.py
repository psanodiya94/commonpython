"""
Additional Edge Case Tests for CommonPython Framework

This test module adds comprehensive edge case and error path testing
to improve code coverage to 95%+ for all modules.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.framework.component_base import ComponentBase  # noqa: E402
from commonpython.framework.component_runner import ComponentRunner  # noqa: E402
from commonpython.database.db2_manager import DB2Manager  # noqa: E402
from commonpython.messaging.mq_manager import MQManager  # noqa: E402


class TestComponentBaseEdgeCases(unittest.TestCase):
    """Edge case tests for ComponentBase"""

    def test_component_initialization_without_dir_in_logging(self):
        """Test component initialization when logging config doesn't have 'dir'"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
database:
  host: localhost
  port: 50000
  name: testdb
messaging:
  host: localhost
  port: 1414
  queue_manager: QM1
logging:
  level: INFO
  file: test.log
  # Note: 'dir' is intentionally omitted to test line 52
""")
            config_file = f.name

        try:

            class TestComp(ComponentBase):
                def initialize(self):
                    pass

                def run(self):
                    pass

                def cleanup(self):
                    pass

            # This should add 'dir' to logging_config
            comp = TestComp("TestCompEdge", config_file=config_file)
            self.assertIsNotNone(comp)
            self.assertIsNotNone(comp.logger_manager)
        finally:
            os.unlink(config_file)

    def test_component_initialization_error(self):
        """Test component initialization with invalid config triggers error path"""
        # Test the exception handler in lines 69-71
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: [[[")
            config_file = f.name

        try:

            class TestCompBad(ComponentBase):
                def initialize(self):
                    pass

                def run(self):
                    pass

                def cleanup(self):
                    pass

            with self.assertRaises(SystemExit):
                TestCompBad("TestCompBad", config_file=config_file)
        finally:
            os.unlink(config_file)

    def test_component_get_config_options(self):
        """Test get_config with required parameter"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
database:
  host: localhost
messaging:
  host: localhost
logging:
  level: INFO
""")
            config_file = f.name

        try:

            class TestCompConfig(ComponentBase):
                def initialize(self):
                    pass

                def run(self):
                    pass

                def cleanup(self):
                    pass

            comp = TestCompConfig("TestCompConfig", config_file=config_file)

            # Test lines related to get_config variations
            value = comp.get_config("database.host")
            self.assertEqual(value, "localhost")

            # Test with default
            value = comp.get_config("nonexistent", "default_value")
            self.assertEqual(value, "default_value")

        finally:
            os.unlink(config_file)


class TestComponentRunnerEdgeCases(unittest.TestCase):
    """Edge case tests for ComponentRunner"""

    def test_component_runner_creation_failure(self):
        """Test component runner when component creation fails"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
database:
  host: localhost
messaging:
  host: localhost
logging:
  level: INFO
""")
            config_file = f.name

        try:

            class FailingComponent(ComponentBase):
                def __init__(self, *args, **kwargs):
                    raise Exception("Creation failed")

                def initialize(self):
                    pass

                def run(self):
                    pass

                def cleanup(self):
                    pass

            runner = ComponentRunner(FailingComponent, "FailingComponent")

            # This should catch the creation exception (line 86)
            with patch("sys.stdout", new=Mock()):
                result = runner.run(["--config", config_file])
                self.assertFalse(result)
        finally:
            os.unlink(config_file)

    def test_component_runner_run_failure(self):
        """Test component runner when run() raises exception"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
database:
  host: localhost
messaging:
  host: localhost
logging:
  level: INFO
""")
            config_file = f.name

        try:

            class FailingRunComponent(ComponentBase):
                def initialize(self):
                    pass

                def run(self):
                    raise Exception("Run failed")

                def cleanup(self):
                    pass

            runner = ComponentRunner(FailingRunComponent, "FailingRunComp")

            # This should catch the run exception (line 103)
            with patch("sys.stdout", new=Mock()):
                result = runner.run(["--config", config_file])
                self.assertFalse(result)
        finally:
            os.unlink(config_file)

    def test_component_runner_keyboard_interrupt(self):
        """Test component runner handling KeyboardInterrupt"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("""
database:
  host: localhost
messaging:
  host: localhost
logging:
  level: INFO
""")
            config_file = f.name

        try:

            class InterruptComponent(ComponentBase):
                def initialize(self):
                    pass

                def run(self):
                    raise KeyboardInterrupt()

                def cleanup(self):
                    pass

            runner = ComponentRunner(InterruptComponent, "InterruptComp")

            # This should catch KeyboardInterrupt (line 131)
            with patch("sys.stdout", new=Mock()):
                result = runner.run(["--config", config_file])
                self.assertFalse(result)
        finally:
            os.unlink(config_file)


class TestDB2ManagerEdgeCases(unittest.TestCase):
    """Edge case tests for DB2Manager"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "host": "localhost",
            "port": 50000,
            "name": "testdb",
            "user": "testuser",
            "password": "testpass",
        }
        self.logger = Mock()
        self.logger.logger = Mock()

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_execute_query_with_params(self, mock_run):
        """Test execute_query with parameters"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        manager = DB2Manager(self.config, self.logger)
        manager.connect()

        # Test with params (line 196)
        mock_run.return_value = Mock(returncode=0, stdout="COL1,COL2\n1,test", stderr="")
        results = manager.execute_query("SELECT * FROM test WHERE id=?", (1,))
        self.assertIsInstance(results, list)

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_execute_update_with_params(self, mock_run):
        """Test execute_update with parameters"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        manager = DB2Manager(self.config, self.logger)
        manager.connect()

        # Test with params (line 205)
        mock_run.return_value = Mock(returncode=0, stdout="1 row affected", stderr="")
        rows = manager.execute_update("UPDATE test SET name=? WHERE id=?", ("test", 1))
        self.assertEqual(rows, 1)

    @patch("commonpython.database.db2_manager.subprocess.run")
    def test_execute_batch_with_params(self, mock_run):
        """Test execute_batch with parameters"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        manager = DB2Manager(self.config, self.logger)
        manager.connect()

        # Test with matching params (tests param handling logic)
        mock_run.return_value = Mock(returncode=0, stdout="1 row affected", stderr="")
        results = manager.execute_batch(["UPDATE test SET name=?", "UPDATE test SET id=?"], [("a",), ("b",)])
        self.assertIsInstance(results, list)


class TestMQManagerEdgeCases(unittest.TestCase):
    """Edge case tests for MQManager"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "host": "localhost",
            "port": 1414,
            "queue_manager": "QM1",
            "channel": "DEV.APP.SVRCONN",
        }
        self.logger = Mock()
        self.logger.logger = Mock()

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_put_message_with_properties(self, mock_run):
        """Test put_message with message properties"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        manager = MQManager(self.config, self.logger)
        manager.connect()

        # Test with properties (line 208)
        mock_run.return_value = Mock(returncode=0, stdout="Message sent", stderr="")
        props = {"priority": 5, "persistence": True}
        result = manager.put_message("TEST.QUEUE", "test message", props)
        self.assertTrue(result)

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_get_message_with_custom_timeout(self, mock_run):
        """Test get_message with custom timeout"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        manager = MQManager(self.config, self.logger)
        manager.connect()

        # Test with custom timeout (line 216-217)
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="No message")
        message = manager.get_message("TEST.QUEUE", timeout=5)
        self.assertIsNone(message)

    @patch("commonpython.messaging.mq_manager.subprocess.run")
    def test_browse_message_with_message_id(self, mock_run):
        """Test browse_message with specific message ID"""
        mock_run.return_value = Mock(returncode=0, stdout="Connected", stderr="")

        manager = MQManager(self.config, self.logger)
        manager.connect()

        # Test with message_id (lines 291-292)
        mock_run.return_value = Mock(returncode=0, stdout="test message", stderr="")
        message = manager.browse_message("TEST.QUEUE", b"MSG_ID_123")
        self.assertIsNotNone(message)


if __name__ == "__main__":
    unittest.main()
