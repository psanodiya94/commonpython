"""
DB2 CLI Adapter for CommonPython Framework

Adapter that wraps the CLI-based DB2Manager implementation and implements
the IDatabaseManager interface. This allows the CLI implementation to be
used interchangeably with library-based implementations.
"""

from contextlib import contextmanager
from typing import Any

from ..database.db2_manager import DB2Manager
from ..interfaces.database_interface import IDatabaseManager


class DB2CLIAdapter(IDatabaseManager):
    """
    Adapter for CLI-based DB2 database operations.

    Wraps the existing DB2Manager (CLI-based) implementation and exposes
    it through the IDatabaseManager interface.
    """

    def __init__(self, config: dict[str, Any], logger=None):
        """
        Initialize the DB2 CLI adapter.

        @brief Initialize adapter with CLI-based DB2Manager.
        @param config Database configuration dictionary
        @param logger Logger manager instance (optional)
        """
        self._impl = DB2Manager(config, logger)
        self._config = config
        self._logger = logger

    def connect(self) -> bool:
        """
        Establish connection to DB2 database using CLI.

        @brief Connect to database via CLI tools.
        @return True if connection successful, False otherwise
        """
        return self._impl.connect()

    def disconnect(self) -> None:
        """
        Close the database connection.

        @brief Disconnect from database via CLI tools.
        """
        self._impl.disconnect()

    def is_connected(self) -> bool:
        """
        Check if database connection is active.

        @brief Check CLI connection status.
        @return True if connected, False otherwise
        """
        return self._impl.is_connected()

    def execute_query(self, query: str, params: tuple | None = None) -> list[dict[str, Any]]:
        """
        Execute a SELECT query and return results.

        @brief Execute SELECT query via CLI and return results.
        @param query SQL query string
        @param params Query parameters (limited support in CLI mode)
        @return List of dictionaries containing query results
        @throws Exception If query execution fails
        """
        return self._impl.execute_query(query, params)

    def execute_update(self, query: str, params: tuple | None = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        @brief Execute DML query via CLI.
        @param query SQL query string
        @param params Query parameters (limited support in CLI mode)
        @return Number of affected rows
        @throws Exception If query execution fails
        """
        return self._impl.execute_update(query, params)

    def execute_batch(
        self, queries: list[str], params_list: list[tuple] | None = None
    ) -> list[int]:
        """
        Execute multiple queries in a batch.

        @brief Execute batch queries via CLI.
        @param queries List of SQL query strings
        @param params_list List of parameter tuples for each query
        @return List of affected rows for each query
        @throws Exception If batch execution fails
        """
        return self._impl.execute_batch(queries, params_list)

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        @brief Provide transaction context via CLI.
        @throws Exception If transaction management fails
        """
        with self._impl.transaction():
            yield self

    def get_table_info(self, table_name: str) -> list[dict[str, Any]]:
        """
        Get table column information.

        @brief Get table metadata via CLI.
        @param table_name Name of the table
        @return List of dictionaries containing column information
        @throws Exception If table info retrieval fails
        """
        return self._impl.get_table_info(table_name)

    def get_database_info(self) -> dict[str, Any]:
        """
        Get database information.

        @brief Get database metadata via CLI.
        @return Dictionary containing database information
        @throws Exception If database info retrieval fails
        """
        return self._impl.get_database_info()

    def test_connection(self) -> bool:
        """
        Test database connection.

        @brief Test CLI database connection.
        @return True if connection is working, False otherwise
        """
        return self._impl.test_connection()
