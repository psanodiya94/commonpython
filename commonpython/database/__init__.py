"""
Database Management Module

Provides IBM DB2 database connectivity and operations using CLI interface with
support for connection management, query execution, transaction management,
result set handling, and error handling using only standard Python modules.

@brief Database functionality for CommonPython Framework
@author CommonPython Framework Team
@version 2.0.0
@since 1.0.0
"""

from .db2_manager import DB2Manager

__all__ = ['DB2Manager']