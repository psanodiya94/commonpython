"""
Database Interface for CommonPython Framework

Defines the abstract interface for database operations that all database
adapters must implement. This allows switching between CLI-based and
library-based implementations without changing client code.
"""

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple


class IDatabaseManager(ABC):
    """
    Abstract interface for database management operations.

    All database adapters (CLI-based, library-based) must implement this interface
    to ensure compatibility with the CommonPython framework.
    """

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the database.

        @brief Connect to database server.
        @return True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close the database connection.

        @brief Disconnect from database server.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if database connection is active.

        @brief Check connection status.
        @return True if connected, False otherwise
        """
        pass

    @abstractmethod
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.

        @brief Execute SELECT query and return results as list of dictionaries.
        @param query SQL query string
        @param params Query parameters tuple for parameterized queries
        @return List of dictionaries containing query results
        @throws Exception If query execution fails
        """
        pass

    @abstractmethod
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        @brief Execute DML query and return affected rows count.
        @param query SQL query string
        @param params Query parameters tuple for parameterized queries
        @return Number of affected rows
        @throws Exception If query execution fails
        """
        pass

    @abstractmethod
    def execute_batch(
        self, queries: List[str], params_list: Optional[List[Tuple]] = None
    ) -> List[int]:
        """
        Execute multiple queries in a batch.

        @brief Execute multiple queries in batch mode.
        @param queries List of SQL query strings
        @param params_list List of parameter tuples for each query
        @return List of affected rows for each query
        @throws Exception If batch execution fails
        """
        pass

    @abstractmethod
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        @brief Provide transaction context for multiple operations.
        @throws Exception If transaction management fails

        Usage:
            with db_manager.transaction():
                db_manager.execute_update("INSERT INTO table VALUES (?)", (value,))
                db_manager.execute_update("UPDATE table SET col = ?", (new_value,))
        """
        pass

    @abstractmethod
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get table column information.

        @brief Get table metadata including column names, types, etc.
        @param table_name Name of the table
        @return List of dictionaries containing column information
        @throws Exception If table info retrieval fails
        """
        pass

    @abstractmethod
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information.

        @brief Get database metadata and system information.
        @return Dictionary containing database information
        @throws Exception If database info retrieval fails
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test database connection.

        @brief Test if database connection is working properly.
        @return True if connection is working, False otherwise
        """
        pass
