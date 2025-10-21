"""
Abstract Interfaces for CommonPython Framework

Provides abstract base classes that define contracts for database, messaging,
and configuration management. This allows switching between different implementations
(CLI-based, library-based, etc.) without changing client code.
"""

from .database_interface import IDatabaseManager
from .messaging_interface import IMessagingManager

__all__ = ['IDatabaseManager', 'IMessagingManager']
