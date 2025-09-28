"""
Configuration Manager for CommonPython Framework

Provides centralized configuration management using only standard Python modules with support for:
- YAML configuration files
- Environment variables
- Default configurations
- Configuration validation
"""

import os
import yaml
from typing import Any, Dict, Optional, Union
from pathlib import Path


class ConfigManager:
    """
    Centralized configuration management for the CommonPython framework.
    
    Supports multiple configuration sources with priority order:
    1. Environment variables
    2. Configuration files
    3. Default values
    """
    
    def __init__(self, config_file: Optional[str] = None, env_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        @brief Initialize configuration manager with file and environment variable support.
        @param config_file Path to YAML configuration file
        @param env_file Path to .env file for environment variables (not used in stdlib version)
        """
        self._config: Dict[str, Any] = {}
        self._config_file = config_file
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Load configuration from file and environment variables. Only fail if config_file is provided and missing.
        """
        if self._config_file:
            if not os.path.exists(self._config_file):
                raise FileNotFoundError(f"Configuration file '{self._config_file}' not found.")
            with open(self._config_file, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file) or {}
        self._load_from_env()
    
    def _load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        
        @brief Load configuration values from environment variables.
        """
        env_mappings = {
            'DB2_HOST': 'database.host',
            'DB2_PORT': 'database.port',
            'DB2_DATABASE': 'database.name',
            'DB2_USER': 'database.user',
            'DB2_PASSWORD': 'database.password',
            'MQ_HOST': 'messaging.host',
            'MQ_PORT': 'messaging.port',
            'MQ_QUEUE_MANAGER': 'messaging.queue_manager',
            'MQ_CHANNEL': 'messaging.channel',
            'LOG_LEVEL': 'logging.level',
            'LOG_FILE': 'logging.file',
            'LOG_FORMAT': 'logging.format'
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config_path, value)
    
    def _set_nested_value(self, path: str, value: Any) -> None:
        """
        Set a nested configuration value using dot notation.
        
        @brief Set configuration value using dot notation path.
        @param path Dot-separated path to configuration value
        @param value Value to set
        """
        keys = path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif value.replace('.', '', 1).isdigit():
                value = float(value)
        
        current[keys[-1]] = value
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get a configuration value using dot notation. If required and missing, raise KeyError.
        """
        keys = key.split('.')
        current = self._config
        try:
            for key_part in keys:
                current = current[key_part]
            if current is None and required:
                raise KeyError(f"Required config key '{key}' is missing.")
            return current
        except (KeyError, TypeError):
            if required:
                raise KeyError(f"Required config key '{key}' is missing.")
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        @brief Set configuration value by key path.
        @param key Configuration key (e.g., 'database.host')
        @param value Value to set
        """
        self._set_nested_value(key, value)
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration with defaults.
        
        @brief Get database configuration with default values if not specified.
        @return Database configuration dictionary
        """
        config = {}
        db_defaults = {
            'host': 'localhost',
            'port': 50000,
            'name': 'testdb',
            'user': 'db2inst1',
            'password': '',
            'schema': '',
            'timeout': 30
        }
        for key, default_value in db_defaults.items():
            config[key] = self.get(f'database.{key}', default_value)
        return config
    
    def get_messaging_config(self) -> Dict[str, Any]:
        """
        Get messaging configuration with defaults.
        
        @brief Get messaging configuration with default values if not specified.
        @return Messaging configuration dictionary
        """
        config = {}
        mq_defaults = {
            'host': 'localhost',
            'port': 1414,
            'queue_manager': 'QM1',
            'channel': 'SYSTEM.DEF.SVRCONN',
            'user': 'mquser',
            'password': '',
            'timeout': 30
        }
        for key, default_value in mq_defaults.items():
            config[key] = self.get(f'messaging.{key}', default_value)
        return config
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration with defaults.
        
        @brief Get logging configuration with default values if not specified.
        @return Logging configuration dictionary
        """
        config = {}
        logging_defaults = {
            'level': 'INFO',
            'file': 'app.log',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'max_size': 10485760,
            'backup_count': 5,
            'dir': 'log',
            'colored': True,
            'json_format': False,
            'console': True
        }
        for key, default_value in logging_defaults.items():
            config[key] = self.get(f'logging.{key}', default_value)
        return config
    
    def reload(self) -> None:
        """
        Reload configuration from files and environment.
        
        @brief Reload configuration from all sources.
        """
        self._config = {}
        self._load_config()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the entire configuration as a dictionary.
        
        @brief Get complete configuration as dictionary.
        @return Dictionary containing all configuration values
        """
        return self._config.copy()
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save current configuration to a YAML file.
        
        @brief Save configuration to YAML file.
        @param file_path Path to save configuration file
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(self._config, file, default_flow_style=False, indent=2)