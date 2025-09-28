"""
Logger Manager for CommonPython Framework

Provides centralized logging functionality using only standard Python modules with support for:
- Multiple log levels
- File and console handlers
- Structured logging with JSON format
- Log rotation
- Custom formatters
"""

import logging
import logging.handlers
import json
import sys
from typing import Any, Dict, Optional, Union
from pathlib import Path
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    @brief Provides JSON formatting for log records using standard Python modules.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        @brief Convert log record to JSON format.
        @param record LogRecord instance to format
        @return JSON string representation of the log record
        """
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class LoggerManager:
    """
    Centralized logging manager for the CommonPython framework.
    
    Provides structured logging with multiple handlers and formatters
    using only standard Python modules.
    """
    
    def __init__(self, name: str = "commonpython", config: Optional[Dict[str, Any]] = None):
        """
        Initialize the logger manager.
        
        @brief Initialize logger with configuration using standard Python modules.
        @param name Logger name
        @param config Logging configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """
        Setup logger with handlers and formatters.
        
        @brief Configure logger with console and file handlers.
        """
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        level = self.config.get('level', 'INFO')
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Prevent duplicate logs
        self.logger.propagate = False
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
    
    def _setup_console_handler(self) -> None:
        """
        Setup console handler with colored output if enabled.
        
        @brief Configure console handler with optional colored output.
        """
        if not self.config.get('console', True):
            return
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config.get('level', 'INFO').upper()))
        # Use colored formatter for console
        if self.config.get('colored', True):
            console_formatter = ColoredFormatter(
                self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
        else:
            console_formatter = logging.Formatter(
                self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self) -> None:
        """
        Setup file handler with rotation.
        
        @brief Configure file handler with log rotation using standard Python modules.
        """
        log_file = self.config.get('file')
        log_dir = self.config.get('dir')
        if not log_file:
            return
        # If log_dir is specified, use it for log file location
        if log_dir:
            log_path = Path(log_dir) / Path(log_file).name
        else:
            log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        max_bytes = self.config.get('max_size', 10 * 1024 * 1024)  # 10MB
        backup_count = self.config.get('backup_count', 5)
        file_handler = logging.handlers.RotatingFileHandler(
            str(log_path), maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        if self.config.get('json_format', True):
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                self.config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance.
        
        @brief Get logger instance by name.
        @param name Logger name (uses main logger if None)
        @return Logger instance
        """
        if name:
            return logging.getLogger(name)
        return self.logger
    
    def log_function_call(self, func_name: str, func_args: tuple = (), func_kwargs: dict = None, 
                         result: Any = None, duration: float = None):
        """
        Log function call with parameters and result.
        
        @brief Log function execution details.
        @param func_name Function name
        @param func_args Function arguments
        @param func_kwargs Function keyword arguments
        @param result Function result
        @param duration Function execution duration
        """
        self.logger.info(
            f"function_call: {func_name}",
            extra={
                'function': func_name,
                'function_args': func_args,
                'function_kwargs': func_kwargs or {},
                'result': result,
                'duration': duration
            }
        )
    
    def log_database_operation(self, operation: str, table: str = None, 
                             query: str = None, duration: float = None, 
                             rows_affected: int = None):
        """
        Log database operation.
        
        @brief Log database operation details.
        @param operation Operation type (SELECT, INSERT, UPDATE, DELETE)
        @param table Table name
        @param query SQL query
        @param duration Operation duration
        @param rows_affected Number of rows affected
        """
        self.logger.info(
            f"database_operation: {operation}",
            extra={
                'operation': operation,
                'table': table,
                'query': query,
                'duration': duration,
                'rows_affected': rows_affected
            }
        )
    
    def log_mq_operation(self, operation: str, queue: str = None, 
                        message_id: str = None, message_size: int = None,
                        duration: float = None):
        """
        Log MQ operation.
        
        @brief Log MQ operation details.
        @param operation Operation type (PUT, GET, BROWSE)
        @param queue Queue name
        @param message_id Message ID
        @param message_size Message size in bytes
        @param duration Operation duration
        """
        self.logger.info(
            f"mq_operation: {operation}",
            extra={
                'operation': operation,
                'queue': queue,
                'message_id': message_id,
                'message_size': message_size,
                'duration': duration
            }
        )
    
    def set_level(self, level: str) -> None:
        """
        Set logging level.
        
        @brief Set logging level for all handlers.
        @param level Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        for handler in self.logger.handlers:
            handler.setLevel(getattr(logging, level.upper(), logging.INFO))


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output.
    
    @brief Provides colored console output using ANSI escape codes.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors.
        
        @brief Add ANSI color codes to log level names.
        @param record LogRecord instance to format
        @return Colored string representation of the log record
        """
        # Get the original formatted message
        message = super().format(record)
        
        # Add color based on log level
        level_name = record.levelname
        if level_name in self.COLORS:
            color = self.COLORS[level_name]
            reset = self.COLORS['RESET']
            message = message.replace(level_name, f"{color}{level_name}{reset}")
        
        return message