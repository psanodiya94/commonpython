"""
Command Line Interface Module

Provides command-line interface functionality with support for database
operations, message queue operations, configuration management, logging control,
and framework testing using only standard Python modules.

@brief CLI functionality for CommonPython Framework
@author CommonPython Framework Team
@version 2.0.0
@since 1.0.0
"""

from .cli import CLI, create_parser, main

__all__ = ['CLI', 'create_parser', 'main']