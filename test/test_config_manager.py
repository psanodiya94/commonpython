"""
Test cases for ConfigManager

Tests configuration management functionality using only standard Python modules.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.config.config_manager import ConfigManager  # noqa: E402


class TestConfigManager(unittest.TestCase):
    """
    Test cases for ConfigManager class.

    @brief Comprehensive test suite for configuration management functionality.
    """

    def setUp(self):
        """
        Set up test fixtures.

        @brief Initialize test environment before each test.
        """
        self.config_manager = ConfigManager()

    def test_init_default(self):
        """
        Test ConfigManager initialization with default parameters.

        @brief Test that ConfigManager initializes correctly with default settings.
        """
        self.assertIsInstance(self.config_manager, ConfigManager)
        self.assertEqual(self.config_manager._config, {})
        self.assertIsNone(self.config_manager._config_file)

    def test_init_with_config_file(self):
        """
        Test ConfigManager initialization with config file.

        @brief Test ConfigManager initialization with configuration file.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            test_config = {"database": {"host": "testhost"}}
            yaml.dump(test_config, f)
            config_file = f.name

        try:
            config_manager = ConfigManager(config_file)
            self.assertEqual(config_manager._config_file, config_file)
        finally:
            os.unlink(config_file)

    def test_set_nested_value(self):
        """
        Test setting nested configuration values.

        @brief Test that nested values can be set using dot notation.
        """
        self.config_manager._set_nested_value("database.host", "localhost")
        self.assertEqual(self.config_manager._config["database"]["host"], "localhost")

        self.config_manager._set_nested_value("logging.level", "DEBUG")
        self.assertEqual(self.config_manager._config["logging"]["level"], "DEBUG")

    def test_set_nested_value_deep(self):
        """
        Test setting deeply nested configuration values.

        @brief Test that deeply nested values can be set.
        """
        self.config_manager._set_nested_value("database.connection.pool.size", 10)
        expected = {"database": {"connection": {"pool": {"size": 10}}}}
        self.assertEqual(self.config_manager._config, expected)

    def test_get_existing_value(self):
        """
        Test getting existing configuration values.

        @brief Test retrieval of existing configuration values.
        """
        self.config_manager._config = {"database": {"host": "localhost", "port": 5432}}

        self.assertEqual(self.config_manager.get("database.host"), "localhost")
        self.assertEqual(self.config_manager.get("database.port"), 5432)

    def test_get_nonexistent_value(self):
        """
        Test getting non-existent configuration values.

        @brief Test retrieval of non-existent values returns default.
        """
        self.assertEqual(self.config_manager.get("nonexistent.key"), None)
        self.assertEqual(self.config_manager.get("nonexistent.key", "default"), "default")

    def test_load_config_file_error(self):
        """
        Test error branch when loading a bad config file.

        @brief Test retrieval of existing configuration file will lead to error.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("bad: [unclosed")
            config_file = f.name
        try:
            with self.assertRaises(Exception):
                ConfigManager(config_file)
        finally:
            os.unlink(config_file)

    def test_set_nested_value_error(self):
        """
        @brief Test error branch for _set_nested_value with bad key (should not raise).
        @return Should set config with empty string key.
        """
        self.config_manager._set_nested_value("", "value")
        self.assertEqual(self.config_manager._config, {"": "value"})

    def test_save_to_file_error(self):
        """
        @brief Test error branch for save_to_file with bad file.
        """
        self.config_manager._config = {"a": 1}
        # Simulate IOError
        with patch("builtins.open", side_effect=IOError):
            with self.assertRaises(IOError):
                self.config_manager.save_to_file("badfile.yaml")

    def test_get_nested_value(self):
        """
        Test getting nested configuration values.

        @brief Test retrieval of nested configuration values.
        """
        self.config_manager._config = {
            "database": {"host": "localhost", "connection": {"timeout": 30}}
        }

        self.assertEqual(self.config_manager.get("database.host"), "localhost")
        self.assertEqual(self.config_manager.get("database.connection.timeout"), 30)

    def test_set_value(self):
        """
        Test setting configuration values.

        @brief Test setting configuration values using dot notation.
        """
        self.config_manager.set("database.host", "testhost")
        self.assertEqual(self.config_manager.get("database.host"), "testhost")

        self.config_manager.set("logging.level", "DEBUG")
        self.assertEqual(self.config_manager.get("logging.level"), "DEBUG")

    def test_get_database_config(self):
        """
        Test getting database configuration.

        @brief Test retrieval of database configuration with defaults.
        """
        config = self.config_manager.get_database_config()

        expected = {
            "host": "localhost",
            "port": 50000,
            "name": "testdb",
            "user": "db2inst1",
            "password": "",
            "schema": "",
            "timeout": 30,
        }

        self.assertEqual(config, expected)

    def test_get_database_config_custom(self):
        """
        Test getting database configuration with custom values.

        @brief Test retrieval of database configuration with custom values.
        """
        self.config_manager.set("database.host", "customhost")
        self.config_manager.set("database.port", 3306)
        self.config_manager.set("database.name", "customdb")

        config = self.config_manager.get_database_config()

        self.assertEqual(config["host"], "customhost")
        self.assertEqual(config["port"], 3306)
        self.assertEqual(config["name"], "customdb")

    def test_get_messaging_config(self):
        """
        Test getting messaging configuration.

        @brief Test retrieval of messaging configuration with defaults.
        """
        config = self.config_manager.get_messaging_config()

        expected = {
            "host": "localhost",
            "port": 1414,
            "queue_manager": "QM1",
            "channel": "SYSTEM.DEF.SVRCONN",
            "user": "mquser",
            "password": "",
            "timeout": 30,
        }

        self.assertEqual(config, expected)

    def test_get_logging_config(self):
        """
        Test getting logging configuration.

        @brief Test retrieval of logging configuration with defaults.
        """
        config = self.config_manager.get_logging_config()

        expected = {
            "level": "INFO",
            "file": "app.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "max_size": 10485760,
            "backup_count": 5,
            "dir": "log",
            "colored": True,
            "json_format": False,
            "console": True,
        }

        self.assertEqual(config, expected)

    @patch.dict(os.environ, {"DB2_HOST": "envhost", "DB2_PORT": "5432", "LOG_LEVEL": "DEBUG"})
    def test_load_from_env(self):
        """
        Test loading configuration from environment variables.

        @brief Test that environment variables override configuration.
        """
        config_manager = ConfigManager()
        config_manager._load_from_env()

        self.assertEqual(config_manager.get("database.host"), "envhost")
        self.assertEqual(config_manager.get("database.port"), 5432)
        self.assertEqual(config_manager.get("logging.level"), "DEBUG")

    def test_to_dict(self):
        """
        Test getting configuration as dictionary.

        @brief Test that to_dict returns a copy of the configuration.
        """
        self.config_manager.set("test.key", "value")
        config_dict = self.config_manager.to_dict()

        self.assertEqual(config_dict["test"]["key"], "value")
        self.assertIsNot(config_dict, self.config_manager._config)  # Should be a copy

    def test_save_to_file(self):
        """
        Test saving configuration to file.

        @brief Test saving configuration to YAML file.
        """
        self.config_manager.set("test.key", "value")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_file = f.name

        try:
            self.config_manager.save_to_file(temp_file)

            with open(temp_file) as f:
                saved_config = yaml.safe_load(f)

            self.assertEqual(saved_config["test"]["key"], "value")
        finally:
            os.unlink(temp_file)

    def test_reload(self):
        """
        Test reloading configuration.

        @brief Test that reload clears and reloads configuration.
        """
        self.config_manager.set("test.key", "value")
        self.assertEqual(self.config_manager.get("test.key"), "value")

        self.config_manager.reload()
        self.assertEqual(self.config_manager.get("test.key"), None)

    def test_type_conversion(self):
        """
        Test automatic type conversion for configuration values.

        @brief Test that string values are converted to appropriate types.
        """
        self.config_manager._set_nested_value("test.bool", "true")
        self.assertEqual(self.config_manager.get("test.bool"), True)

        self.config_manager._set_nested_value("test.int", "123")
        self.assertEqual(self.config_manager.get("test.int"), 123)

        self.config_manager._set_nested_value("test.float", "123.45")
        self.assertEqual(self.config_manager.get("test.float"), 123.45)

        self.config_manager._set_nested_value("test.string", "hello")
        self.assertEqual(self.config_manager.get("test.string"), "hello")
