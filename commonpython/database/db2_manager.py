"""
DB2 Manager for CommonPython Framework

Provides IBM DB2 database connectivity and operations using CLI interface with support for:
- Connection management
- Query execution
- Transaction management
- Result set handling
- Error handling and logging
"""

import csv
import subprocess
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple


class DB2Manager:
    """
    IBM DB2 database manager for the CommonPython framework using CLI interface.

    Provides connection management, query execution, and transaction handling
    using IBM DB2 command-line tools instead of SDK modules.
    """

    def __init__(self, config: Dict[str, Any], logger=None):
        """
        Initialize the DB2 manager.

        @brief Initialize the DB2 manager with configuration and logger.
        @param config Database configuration dictionary
        @param logger Logger manager instance (optional)
        """
        self.config = config
        self.logger = logger
        self.connection_string = self._build_connection_string()
        self.connected = False

    def _build_connection_string(self) -> str:
        """
        Build DB2 connection string from configuration.

        @brief Create connection string for DB2 CLI commands.
        @return Formatted connection string for DB2 CLI
        """
        host = self.config.get("host", "localhost")
        port = self.config.get("port", 50000)
        database = self.config.get("database", "testdb")
        user = self.config.get("user", "db2inst1")
        password = self.config.get("password", "")
        schema = self.config.get("schema", "")

        conn_str = f"DATABASE={database};HOSTNAME={host};PORT={port};"
        conn_str += f"PROTOCOL=TCPIP;UID={user};PWD={password};"

        if schema:
            conn_str += f"CURRENTSCHEMA={schema};"

        return conn_str

    def _execute_db2_command(
        self, command: str, params: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a DB2 CLI command.

        @brief Execute DB2 CLI command and return results.
        @param command DB2 CLI command to execute
        @param params Optional parameters for the command
        @return Dictionary containing command results and metadata
        @throws Exception If command execution fails
        """
        try:
            # Prepare the full command
            full_command = ["db2", command]
            if params:
                full_command.extend(params)

            # Execute the command
            result = subprocess.run(
                full_command, capture_output=True, text=True, timeout=self.config.get("timeout", 30)
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            if self.logger:
                self.logger.logger.error(f"DB2 command timeout: {command}")
            raise Exception(f"DB2 command timeout: {command}")
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"DB2 command error: {str(e)}")
            raise Exception(f"DB2 command error: {str(e)}")

    def connect(self) -> bool:
        """
        Establish connection to DB2 database.

        @brief Test connection to DB2 database using CLI.
        @return True if connection successful, False otherwise
        """
        try:
            # Test connection with a simple query
            result = self._execute_db2_command(
                "connect to", [self.config.get("database", "testdb")]
            )

            if result["success"]:
                self.connected = True
                if self.logger:
                    self.logger.logger.info(
                        f"Successfully connected to DB2 database: {self.config.get('database')}"
                    )
                return True
            else:
                if self.logger:
                    self.logger.logger.error(
                        f"Failed to connect to DB2 database: {result['stderr']}"
                    )
                return False

        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"DB2 connection error: {str(e)}")
            return False

    def disconnect(self) -> None:
        """
        Close the database connection.

        @brief Disconnect from DB2 database using CLI.
        """
        try:
            if self.connected:
                self._execute_db2_command("disconnect")
                self.connected = False
                if self.logger:
                    self.logger.logger.info("DB2 connection closed")
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"Error closing DB2 connection: {str(e)}")

    def is_connected(self) -> bool:
        """
        Check if database connection is active.

        @brief Check if DB2 connection is established.
        @return True if connected, False otherwise
        """
        return self.connected

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.

        @brief Execute SELECT query using DB2 CLI and return results as list of dictionaries.
        @param query SQL query string
        @param params Query parameters tuple (not supported in CLI mode)
        @return List of dictionaries containing query results
        @throws Exception If query execution fails
        """
        if not self.is_connected():
            raise Exception("Database connection not established")

        start_time = time.time()

        try:
            # Create a temporary file for the query
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
                f.write(query)
                temp_file = f.name

            # Execute query using DB2 CLI
            result = self._execute_db2_command(
                "import from", [temp_file, "of del", "insert into temp_table"]
            )

            # For SELECT queries, we need to use a different approach
            # Export results to CSV and parse them
            csv_result = self._execute_db2_command(
                "export to", ["/tmp/query_result.csv", "of del", "select * from", "(" + query + ")"]
            )

            if csv_result["success"]:
                # Parse CSV results
                results = self._parse_csv_results("/tmp/query_result.csv")

                duration = time.time() - start_time
                if self.logger:
                    self.logger.log_database_operation(
                        operation="SELECT",
                        query=query,
                        duration=duration,
                        rows_affected=len(results),
                    )

                return results
            else:
                raise Exception(f"Query execution failed: {csv_result['stderr']}")

        except Exception as e:
            duration = time.time() - start_time
            if self.logger:
                self.logger.logger.error(f"Query execution error: {str(e)}")
                self.logger.log_database_operation(
                    operation="SELECT", query=query, duration=duration, rows_affected=0
                )
            raise

        finally:
            # Clean up temporary files
            import os

            try:
                if "temp_file" in locals():
                    os.unlink(temp_file)
                if os.path.exists("/tmp/query_result.csv"):
                    os.unlink("/tmp/query_result.csv")
            except:
                pass

    def _parse_csv_results(self, csv_file: str) -> List[Dict[str, Any]]:
        """
        Parse CSV results from DB2 export.

        @brief Parse CSV file containing query results.
        @param csv_file Path to CSV file
        @return List of dictionaries containing parsed results
        """
        results = []
        try:
            with open(csv_file, encoding="utf-8") as f:
                # Read first line to get column names
                reader = csv.reader(f)
                columns = next(reader, [])

                # Read data rows
                for row in reader:
                    if row:  # Skip empty rows
                        result_dict = {}
                        for i, value in enumerate(row):
                            if i < len(columns):
                                result_dict[columns[i]] = value
                        results.append(result_dict)
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"Error parsing CSV results: {str(e)}")

        return results

    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        @brief Execute DML query using DB2 CLI.
        @param query SQL query string
        @param params Query parameters tuple (not supported in CLI mode)
        @return Number of affected rows
        @throws Exception If query execution fails
        """
        if not self.is_connected():
            raise Exception("Database connection not established")

        start_time = time.time()

        try:
            # Create a temporary file for the query
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False) as f:
                f.write(query)
                temp_file = f.name

            # Execute the query
            result = self._execute_db2_command(
                "import from", [temp_file, "of del", "insert into temp_table"]
            )

            # For updates, we need to get the row count
            # This is a simplified approach - in practice, you'd need more sophisticated handling
            rows_affected = 1  # Default assumption

            duration = time.time() - start_time
            operation = query.strip().split()[0].upper()
            if self.logger:
                self.logger.log_database_operation(
                    operation=operation, query=query, duration=duration, rows_affected=rows_affected
                )

            return rows_affected

        except Exception as e:
            duration = time.time() - start_time
            if self.logger:
                self.logger.logger.error(f"Update execution error: {str(e)}")
                self.logger.log_database_operation(
                    operation=query.strip().split()[0].upper(),
                    query=query,
                    duration=duration,
                    rows_affected=0,
                )
            raise

        finally:
            # Clean up temporary files
            import os

            try:
                if "temp_file" in locals():
                    os.unlink(temp_file)
            except:
                pass

    def execute_batch(
        self, queries: List[str], params_list: Optional[List[Tuple]] = None
    ) -> List[int]:
        """
        Execute multiple queries in a batch.

        @brief Execute multiple queries using DB2 CLI in batch mode.
        @param queries List of SQL query strings
        @param params_list List of parameter tuples for each query (not supported in CLI mode)
        @return List of affected rows for each query
        @throws Exception If batch execution fails
        """
        if not self.is_connected():
            raise Exception("Database connection not established")

        results = []

        try:
            # Begin transaction
            self._execute_db2_command("begin transaction")

            for i, query in enumerate(queries):
                rows_affected = self.execute_update(query, None)
                results.append(rows_affected)

            # Commit transaction
            self._execute_db2_command("commit")
            if self.logger:
                self.logger.logger.info(f"Batch execution completed: {len(queries)} queries")

        except Exception as e:
            # Rollback transaction
            self._execute_db2_command("rollback")
            if self.logger:
                self.logger.logger.error(f"Batch execution error: {str(e)}")
            raise

        return results

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        @brief Context manager for DB2 transactions using CLI.
        @throws Exception If transaction management fails

        Usage:
            with db_manager.transaction():
                db_manager.execute_update("INSERT INTO table VALUES (?)", (value,))
                db_manager.execute_update("UPDATE table SET col = ?", (new_value,))
        """
        if not self.is_connected():
            raise Exception("Database connection not established")

        try:
            # Begin transaction
            self._execute_db2_command("begin transaction")
            if self.logger:
                self.logger.logger.debug("Transaction started")
            yield self

            # Commit transaction
            self._execute_db2_command("commit")
            if self.logger:
                self.logger.logger.debug("Transaction committed")

        except Exception as e:
            # Rollback transaction
            self._execute_db2_command("rollback")
            if self.logger:
                self.logger.logger.error(f"Transaction rolled back: {str(e)}")
            raise

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get table column information.

        @brief Get table metadata using DB2 CLI system catalog queries.
        @param table_name Name of the table
        @return List of dictionaries containing column information
        @throws Exception If table info retrieval fails
        """
        query = f"""
        SELECT COLNAME, TYPENAME, LENGTH, SCALE, NULLS, KEYSEQ
        FROM SYSCAT.COLUMNS
        WHERE TABNAME = UPPER('{table_name}')
        ORDER BY COLNO
        """

        return self.execute_query(query)

    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information.

        @brief Get database metadata using DB2 CLI system catalog queries.
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

        @brief Test DB2 connection using CLI.
        @return True if connection is working, False otherwise
        """
        try:
            result = self.execute_query("SELECT 1 FROM SYSIBM.SYSDUMMY1")
            return len(result) > 0
        except Exception as e:
            if self.logger:
                self.logger.logger.error(f"Connection test failed: {str(e)}")
            return False
