"""
CLI Interface for CommonPython Framework

Provides command-line interface using only standard Python modules with support for:
- Database operations
- Message queue operations
- Configuration management
- Logging control
- Framework testing
"""

import argparse
import json
import sys
from typing import Any, Optional


class CLI:
    """
    Command-line interface for the CommonPython framework.

    Provides interactive and non-interactive access to framework functionality
    using only standard Python modules.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the CLI.

        @brief Initialize CLI with configuration file support.
        @param config_file Path to configuration file
        """
        self.config_file = config_file
        self.config_manager = None
        self.logger_manager = None
        self.db_manager = None
        self.mq_manager = None

        # Initialize components
        self._initialize_components()

    def _initialize_components(self) -> None:
        """
        Initialize framework components.

        @brief Initialize configuration, logging, database, and messaging managers.
        """
        try:
            from ..config import ConfigManager
            from ..database import DB2Manager
            from ..logging import LoggerManager
            from ..messaging import MQManager

            self.config_manager = ConfigManager(self.config_file)
            logging_config = self.config_manager.get_logging_config()
            if "dir" not in logging_config:
                logging_config["dir"] = "log"
            self.logger_manager = LoggerManager("cli", logging_config)

            # Initialize managers but don't connect yet
            db_config = self.config_manager.get_database_config()
            mq_config = self.config_manager.get_messaging_config()

            self.db_manager = DB2Manager(db_config, self.logger_manager)
            self.mq_manager = MQManager(mq_config, self.logger_manager)

        except ImportError as e:
            print(f"Error importing modules: {e}")
            sys.exit(1)

    def _setup_database(self) -> bool:
        """
        Setup database connection.

        @brief Establish database connection.
        @return True if connection successful, False otherwise
        """
        try:
            return self.db_manager.connect()
        except Exception as e:
            print(f"Database setup failed: {str(e)}")
            return False

    def _setup_messaging(self) -> bool:
        """
        Setup messaging connection.

        @brief Establish messaging connection.
        @return True if connection successful, False otherwise
        """
        try:
            return self.mq_manager.connect()
        except Exception as e:
            print(f"Messaging setup failed: {str(e)}")
            return False

    def _display_results(self, results: Any, title: str = "Results") -> None:
        """
        Display results in a formatted table.

        @brief Display results in a readable format.
        @param results Results to display
        @param title Title for the results
        """
        if not results:
            print(f"No {title.lower()} found")
            return

        print(f"\n{title}:")
        print("=" * len(title))

        if isinstance(results, list) and results and isinstance(results[0], dict):
            # Display as table
            if results:
                # Get column headers
                headers = list(results[0].keys())

                # Calculate column widths
                col_widths = {}
                for header in headers:
                    col_widths[header] = max(
                        len(str(header)), max(len(str(row.get(header, ""))) for row in results)
                    )

                # Print header
                header_row = " | ".join(header.ljust(col_widths[header]) for header in headers)
                print(header_row)
                print("-" * len(header_row))

                # Print rows
                for row in results:
                    row_data = " | ".join(
                        str(row.get(header, "")).ljust(col_widths[header]) for header in headers
                    )
                    print(row_data)
        else:
            # Display as JSON
            print(json.dumps(results, indent=2, default=str))

    def test_database(self) -> None:
        """
        Test database connection.

        @brief Test database connection and display results.
        """
        print("Testing database connection...")

        if self._setup_database():
            if self.db_manager.test_connection():
                print("✓ Database connection successful")
            else:
                print("✗ Database connection failed")
        else:
            print("✗ Database setup failed")

    def execute_query(self, query: str, params: Optional[str] = None) -> None:
        """
        Execute a database query.

        @brief Execute database query and display results.
        @param query SQL query to execute
        @param params Query parameters as JSON string
        """
        if not self._setup_database():
            sys.exit(1)

        try:
            # Parse parameters if provided
            query_params = None
            if params:
                query_params = tuple(json.loads(params))

            # Execute query
            if query.strip().upper().startswith("SELECT"):
                results = self.db_manager.execute_query(query, query_params)
                self._display_results(results, "Query Results")
            else:
                rows_affected = self.db_manager.execute_update(query, query_params)
                print(f"Query executed successfully. Rows affected: {rows_affected}")

        except Exception as e:
            print(f"Query execution failed: {str(e)}")
            sys.exit(1)

    def get_table_info(self, table_name: str) -> None:
        """
        Get table information.

        @brief Get table metadata and display results.
        @param table_name Name of the table
        """
        if not self._setup_database():
            sys.exit(1)

        try:
            results = self.db_manager.get_table_info(table_name)
            self._display_results(results, f"Table Information: {table_name}")
        except Exception as e:
            print(f"Failed to get table info: {str(e)}")
            sys.exit(1)

    def test_messaging(self) -> None:
        """
        Test MQ connection.

        @brief Test messaging connection and display results.
        """
        print("Testing MQ connection...")

        if self._setup_messaging():
            if self.mq_manager.test_connection():
                print("✓ MQ connection successful")
            else:
                print("✗ MQ connection failed")
        else:
            print("✗ MQ setup failed")

    def get_message(self, queue_name: str, timeout: Optional[int] = None) -> None:
        """
        Get a message from queue.

        @brief Get message from queue and display results.
        @param queue_name Name of the queue
        @param timeout Timeout in seconds
        """
        if not self._setup_messaging():
            sys.exit(1)

        try:
            message = self.mq_manager.get_message(queue_name, timeout)
            if message:
                self._display_results(message, f"Message from {queue_name}")
            else:
                print(f"No message available in queue {queue_name}")
        except Exception as e:
            print(f"Failed to get message: {str(e)}")
            sys.exit(1)

    def put_message(self, queue_name: str, message: str, properties: Optional[str] = None) -> None:
        """
        Put a message to queue.

        @brief Send message to queue.
        @param queue_name Name of the queue
        @param message Message content
        @param properties Message properties as JSON string
        """
        if not self._setup_messaging():
            sys.exit(1)
        try:
            # Parse message properties if provided
            message_properties = None
            if properties:
                try:
                    message_properties = json.loads(properties)
                except json.JSONDecodeError:
                    message_properties = None
            # Try to parse message as JSON, fallback to string
            try:
                message_data = json.loads(message)
            except json.JSONDecodeError:
                message_data = message
            success = self.mq_manager.put_message(queue_name, message_data, message_properties)
            if success:
                print(f"Message sent to queue {queue_name}")
            else:
                print(f"Failed to send message to queue {queue_name}")
                sys.exit(1)
        except Exception as e:
            print(f"Failed to put message: {str(e)}")
            sys.exit(1)

    def get_queue_depth(self, queue_name: str) -> None:
        """
        Get queue depth.

        @brief Get queue depth and display results.
        @param queue_name Name of the queue
        """
        if not self._setup_messaging():
            sys.exit(1)

        try:
            depth = self.mq_manager.get_queue_depth(queue_name)
            if depth >= 0:
                print(f"Queue {queue_name} depth: {depth}")
            else:
                print("Failed to get queue depth")
                sys.exit(1)
        except Exception as e:
            print(f"Failed to get queue depth: {str(e)}")
            sys.exit(1)

    def show_config(self) -> None:
        """
        Show current configuration.

        @brief Display current configuration.
        """
        config_dict = self.config_manager.to_dict()
        self._display_results(config_dict, "Current Configuration")

    def get_config(self, key: str) -> None:
        """
        Get a configuration value.

        @brief Get specific configuration value.
        @param key Configuration key
        """
        value = self.config_manager.get(key)
        print(f"{key}: {value}")

    def set_config(self, key: str, value: str) -> None:
        """
        Set a configuration value.

        @brief Set configuration value.
        @param key Configuration key
        @param value Configuration value
        """
        self.config_manager.set(key, value)
        print(f"Set {key} = {value}")

    def test_all(self) -> None:
        """
        Test all framework components.

        @brief Test all framework components and display results.
        """
        results = {}

        # Test database
        print("Testing database...")
        results["database"] = self._setup_database() and self.db_manager.test_connection()

        # Test messaging
        print("Testing messaging...")
        results["messaging"] = self._setup_messaging() and self.mq_manager.test_connection()

        # Display results
        print("\nFramework Test Results:")
        print("=" * 25)
        for component, status in results.items():
            status_text = "✓ PASS" if status else "✗ FAIL"
            print(f"{component.title()}: {status_text}")


def create_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.

    @brief Create argument parser for CLI commands.
    @return Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(description="CommonPython Framework CLI")
    parser.add_argument("--config", "-c", help="Configuration file path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Database commands
    db_parser = subparsers.add_parser("database", help="Database operations")
    db_subparsers = db_parser.add_subparsers(dest="db_command", help="Database commands")

    db_subparsers.add_parser("test", help="Test database connection")

    db_exec_parser = db_subparsers.add_parser("execute", help="Execute database query")
    db_exec_parser.add_argument("query", help="SQL query to execute")
    db_exec_parser.add_argument("--params", "-p", help="Query parameters as JSON string")

    db_info_parser = db_subparsers.add_parser("info", help="Get table information")
    db_info_parser.add_argument("table_name", help="Name of the table")

    # Messaging commands
    mq_parser = subparsers.add_parser("messaging", help="Message queue operations")
    mq_subparsers = mq_parser.add_subparsers(dest="mq_command", help="Messaging commands")

    mq_subparsers.add_parser("test", help="Test MQ connection")

    mq_get_parser = mq_subparsers.add_parser("get", help="Get message from queue")
    mq_get_parser.add_argument("queue_name", help="Name of the queue")
    mq_get_parser.add_argument("--timeout", "-t", type=int, help="Timeout in seconds")

    mq_put_parser = mq_subparsers.add_parser("put", help="Put message to queue")
    mq_put_parser.add_argument("queue_name", help="Name of the queue")
    mq_put_parser.add_argument("message", help="Message content")
    mq_put_parser.add_argument("--properties", "-p", help="Message properties as JSON string")

    mq_depth_parser = mq_subparsers.add_parser("depth", help="Get queue depth")
    mq_depth_parser.add_argument("queue_name", help="Name of the queue")

    # Configuration commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(
        dest="config_command", help="Configuration commands"
    )

    config_subparsers.add_parser("show", help="Show current configuration")

    config_get_parser = config_subparsers.add_parser("get", help="Get configuration value")
    config_get_parser.add_argument("key", help="Configuration key")

    config_set_parser = config_subparsers.add_parser("set", help="Set configuration value")
    config_set_parser.add_argument("key", help="Configuration key")
    config_set_parser.add_argument("value", help="Configuration value")

    # Test all command
    subparsers.add_parser("test-all", help="Test all framework components")

    return parser


def main():
    """
    Main CLI entry point.

    @brief Main entry point for CLI application.
    """
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = None
    try:
        if args.command != "help":
            cli = CLI(args.config)

        if args.command == "database":
            if args.db_command == "test":
                cli.test_database()
            elif args.db_command == "execute":
                cli.execute_query(args.query, args.params)
            elif args.db_command == "info":
                cli.get_table_info(args.table_name)

        elif args.command == "messaging":
            if args.mq_command == "test":
                cli.test_messaging()
            elif args.mq_command == "get":
                cli.get_message(args.queue_name, args.timeout)
            elif args.mq_command == "put":
                cli.put_message(args.queue_name, args.message, args.properties)
            elif args.mq_command == "depth":
                cli.get_queue_depth(args.queue_name)

        elif args.command == "config":
            if args.config_command == "show":
                cli.show_config()
            elif args.config_command == "get":
                cli.get_config(args.key)
            elif args.config_command == "set":
                cli.set_config(args.key, args.value)

        elif args.command == "test-all":
            cli.test_all()

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
