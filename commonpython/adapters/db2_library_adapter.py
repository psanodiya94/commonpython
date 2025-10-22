"""
DB2 Library Adapter for CommonPython Framework

Adapter that uses the ibm_db Python library for DB2 database operations.
Implements the IDatabaseManager interface for library-based access.
"""

import time
from contextlib import contextmanager
from typing import Any

from ..interfaces.database_interface import IDatabaseManager

# Try to import ibm_db library
try:
    import ibm_db
    import ibm_db_dbi

    HAS_IBM_DB = True
except ImportError:
    HAS_IBM_DB = False


class DB2LibraryAdapter(IDatabaseManager):
    """
    Adapter for library-based DB2 database operations using ibm_db.

    Provides efficient, native DB2 connectivity using the ibm_db Python library
    with support for connection pooling, prepared statements, and proper
    parameterized queries.
    """

    def __init__(self, config: dict[str, Any], logger=None):
        """
        Initialize the DB2 library adapter.

        @brief Initialize adapter with ibm_db library.
        @param config Database configuration dictionary
        @param logger Logger manager instance (optional)
        @throws ImportError If ibm_db library is not installed
        """
        if not HAS_IBM_DB:
            raise ImportError(
                "ibm_db library is not installed. " "Install it with: pip install ibm_db"
            )

        self._config = config
        self._logger = logger
        self._conn = None
        self._dbi_conn = None
        self._connection_string = self._build_connection_string()

    def _build_connection_string(self) -> str:
        """
        Build DB2 connection string from configuration.

        @brief Create connection string for ibm_db.
        @return Formatted connection string
        """
        host = self._config.get("host", "localhost")
        port = self._config.get("port", 50000)
        database = self._config.get("database", self._config.get("name", "testdb"))
        user = self._config.get("user", "db2inst1")
        password = self._config.get("password", "")
        schema = self._config.get("schema", "")

        conn_str = f"DATABASE={database};HOSTNAME={host};PORT={port};"
        conn_str += f"PROTOCOL=TCPIP;UID={user};PWD={password};"

        if schema:
            conn_str += f"CURRENTSCHEMA={schema};"

        return conn_str

    def connect(self) -> bool:
        """
        Establish connection to DB2 database using ibm_db library.

        @brief Connect to database via ibm_db library.
        @return True if connection successful, False otherwise
        """
        try:
            self._conn = ibm_db.connect(self._connection_string, "", "")
            self._dbi_conn = ibm_db_dbi.Connection(self._conn)

            if self._logger:
                self._logger.logger.info(
                    f"Successfully connected to DB2 database: {self._config.get('database', self._config.get('name'))}"
                )
            return True

        except Exception as e:
            if self._logger:
                self._logger.logger.error(f"DB2 connection error: {str(e)}")
            return False

    def disconnect(self) -> None:
        """
        Close the database connection.

        @brief Disconnect from database via ibm_db library.
        """
        try:
            if self._dbi_conn:
                self._dbi_conn.close()
                self._dbi_conn = None

            if self._conn:
                ibm_db.close(self._conn)
                self._conn = None

            if self._logger:
                self._logger.logger.info("DB2 connection closed")

        except Exception as e:
            if self._logger:
                self._logger.logger.error(f"Error closing DB2 connection: {str(e)}")

    def is_connected(self) -> bool:
        """
        Check if database connection is active.

        @brief Check ibm_db connection status.
        @return True if connected, False otherwise
        """
        try:
            if self._conn and ibm_db.active(self._conn):
                return True
        except Exception:
            pass
        return False

    def execute_query(self, query: str, params: tuple | None = None) -> list[dict[str, Any]]:
        """
        Execute a SELECT query and return results.

        @brief Execute SELECT query via ibm_db with parameterization support.
        @param query SQL query string (use ? for parameters)
        @param params Query parameters tuple
        @return List of dictionaries containing query results
        @throws Exception If query execution fails
        """
        if not self.is_connected():
            raise Exception("Database connection not established")

        start_time = time.time()
        results = []

        try:
            cursor = self._dbi_conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch all rows
            for row in cursor.fetchall():
                result_dict = {}
                for i, value in enumerate(row):
                    if i < len(columns):
                        result_dict[columns[i]] = value
                results.append(result_dict)

            cursor.close()

            duration = time.time() - start_time
            if self._logger:
                self._logger.log_database_operation(
                    operation="SELECT", query=query, duration=duration, rows_affected=len(results)
                )

            return results

        except Exception as e:
            duration = time.time() - start_time
            if self._logger:
                self._logger.logger.error(f"Query execution error: {str(e)}")
                self._logger.log_database_operation(
                    operation="SELECT", query=query, duration=duration, rows_affected=0
                )
            raise

    def execute_update(self, query: str, params: tuple | None = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        @brief Execute DML query via ibm_db with parameterization support.
        @param query SQL query string (use ? for parameters)
        @param params Query parameters tuple
        @return Number of affected rows
        @throws Exception If query execution fails
        """
        if not self.is_connected():
            raise Exception("Database connection not established")

        start_time = time.time()

        try:
            cursor = self._dbi_conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            rows_affected = cursor.rowcount
            cursor.close()

            # Auto-commit for non-transactional updates
            self._dbi_conn.commit()

            duration = time.time() - start_time
            operation = query.strip().split()[0].upper()
            if self._logger:
                self._logger.log_database_operation(
                    operation=operation, query=query, duration=duration, rows_affected=rows_affected
                )

            return rows_affected

        except Exception as e:
            duration = time.time() - start_time
            if self._logger:
                self._logger.logger.error(f"Update execution error: {str(e)}")
                self._logger.log_database_operation(
                    operation=query.strip().split()[0].upper(),
                    query=query,
                    duration=duration,
                    rows_affected=0,
                )
            raise

    def execute_batch(
        self, queries: list[str], params_list: list[tuple] | None = None
    ) -> list[int]:
        """
        Execute multiple queries in a batch.

        @brief Execute batch queries via ibm_db within a transaction.
        @param queries List of SQL query strings
        @param params_list List of parameter tuples for each query
        @return List of affected rows for each query
        @throws Exception If batch execution fails
        """
        if not self.is_connected():
            raise Exception("Database connection not established")

        results = []

        try:
            # Begin transaction
            cursor = self._dbi_conn.cursor()

            for i, query in enumerate(queries):
                params = params_list[i] if params_list and i < len(params_list) else None

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                results.append(cursor.rowcount)

            cursor.close()

            # Commit transaction
            self._dbi_conn.commit()

            if self._logger:
                self._logger.logger.info(f"Batch execution completed: {len(queries)} queries")

        except Exception as e:
            # Rollback transaction
            self._dbi_conn.rollback()
            if self._logger:
                self._logger.logger.error(f"Batch execution error: {str(e)}")
            raise

        return results

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        @brief Provide transaction context via ibm_db.
        @throws Exception If transaction management fails
        """
        if not self.is_connected():
            raise Exception("Database connection not established")

        try:
            # ibm_db_dbi uses auto-commit by default, we disable it for transaction
            if self._logger:
                self._logger.logger.debug("Transaction started")

            yield self

            # Commit transaction
            self._dbi_conn.commit()
            if self._logger:
                self._logger.logger.debug("Transaction committed")

        except Exception as e:
            # Rollback transaction
            self._dbi_conn.rollback()
            if self._logger:
                self._logger.logger.error(f"Transaction rolled back: {str(e)}")
            raise

    def get_table_info(self, table_name: str) -> list[dict[str, Any]]:
        """
        Get table column information.

        @brief Get table metadata using ibm_db system catalog.
        @param table_name Name of the table
        @return List of dictionaries containing column information
        @throws Exception If table info retrieval fails
        """
        query = """
        SELECT COLNAME, TYPENAME, LENGTH, SCALE, NULLS, KEYSEQ
        FROM SYSCAT.COLUMNS
        WHERE TABNAME = ?
        ORDER BY COLNO
        """

        return self.execute_query(query, (table_name.upper(),))

    def get_database_info(self) -> dict[str, Any]:
        """
        Get database information.

        @brief Get database metadata using ibm_db system catalog.
        @return Dictionary containing database information
        @throws Exception If database info retrieval fails
        """
        query = "SELECT * FROM SYSIBMADM.ENV_INST_INFO"
        result = self.execute_query(query)

        if result:
            return result[0]
        return {}

    def test_connection(self) -> bool:
        """
        Test database connection.

        @brief Test ibm_db connection.
        @return True if connection is working, False otherwise
        """
        try:
            result = self.execute_query("SELECT 1 FROM SYSIBM.SYSDUMMY1")
            return len(result) > 0
        except Exception as e:
            if self._logger:
                self._logger.logger.error(f"Connection test failed: {str(e)}")
            return False
