"""
CommonPython Framework

A comprehensive Python framework providing configuration management, logging,
database connectivity, message queue operations, and command-line interface
functionality using only standard Python modules and IBM CLI interfaces.

@brief Main package for CommonPython Framework
@author CommonPython Framework Team
@version 2.0.0
@since 1.0.0
"""

__version__ = "2.0.0"
__author__ = "CommonPython Framework Team"
__email__ = "team@commonpython.com"
__description__ = "A common Python framework using only standard modules and IBM CLI interfaces"

# Import main components for easy access
from .config import ConfigManager
from .logging import LoggerManager
from .database import DB2Manager
from .messaging import MQManager
from .cli import CLI

# Import exception classes
from .exceptions import (
    CommonPythonError,
    ConfigurationError,
    DatabaseError,
    MessagingError,
    AdapterError,
    ComponentError,
)

__all__ = [
    'ConfigManager',
    'LoggerManager',
    'DB2Manager',
    'MQManager',
    'CLI',
    'CommonPythonError',
    'ConfigurationError',
    'DatabaseError',
    'MessagingError',
    'AdapterError',
    'ComponentError',
]