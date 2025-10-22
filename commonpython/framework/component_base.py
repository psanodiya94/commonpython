"""
Component Base Class for CommonPython Framework

Provides base functionality for components that want to use the CommonPython framework.
"""

import sys
from abc import ABC, abstractmethod
from typing import Any

from ..config import ConfigManager
from ..factories import ManagerFactory
from ..logging import LoggerManager


class ComponentBase(ABC):
    """
    Base class for components using CommonPython framework.

    Provides common functionality including configuration, logging, database,
    and messaging capabilities to any component that inherits from this class.
    """

    def __init__(self, component_name: str, config_file: str | None = None):
        """
        Initialize the component.

        @brief Initialize component with CommonPython framework services.
        @param component_name Name of the component
        @param config_file Path to configuration file (optional)
        """
        self.component_name = component_name
        self.config_file = config_file

        # Initialize framework services
        self._initialize_services()

    def _initialize_services(self) -> None:
        """
        Initialize CommonPython framework services.

        @brief Setup configuration, logging, database, and messaging services.
        """
        try:
            # Initialize configuration
            self.config_manager = ConfigManager(self.config_file)

            # Initialize logging
            logging_config = self.config_manager.get_logging_config()
            logging_config["file"] = f"{self.component_name}.log"
            if "dir" not in logging_config:
                logging_config["dir"] = "log"
            self.logger_manager = LoggerManager(self.component_name, logging_config)

            # Initialize database manager using factory
            db_config = self.config_manager.get_database_config()
            self.db_manager = ManagerFactory.create_database_manager(db_config, self.logger_manager)

            # Initialize messaging manager using factory
            mq_config = self.config_manager.get_messaging_config()
            self.mq_manager = ManagerFactory.create_messaging_manager(
                mq_config, self.logger_manager
            )

            self.logger_manager.logger.info(
                f"Component '{self.component_name}' initialized successfully"
            )

        except Exception as e:
            print(f"Error initializing component '{self.component_name}': {str(e)}")
            sys.exit(1)

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        @brief Get configuration value by key.
        @param key Configuration key
        @param default Default value if key not found
        @return Configuration value
        """
        return self.config_manager.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        @brief Set configuration value by key.
        @param key Configuration key
        @param value Value to set
        """
        self.config_manager.set(key, value)

    def log_info(self, message: str, **kwargs) -> None:
        """
        Log info message.

        @brief Log informational message.
        @param message Message to log
        @param kwargs Additional log data
        """
        self.logger_manager.logger.info(message, extra=kwargs)

    def log_error(self, message: str, **kwargs) -> None:
        """
        Log error message.

        @brief Log error message.
        @param message Message to log
        @param kwargs Additional log data
        """
        self.logger_manager.logger.error(message, extra=kwargs)

    def log_warning(self, message: str, **kwargs) -> None:
        """
        Log warning message.

        @brief Log warning message.
        @param message Message to log
        @param kwargs Additional log data
        """
        self.logger_manager.logger.warning(message, extra=kwargs)

    def log_debug(self, message: str, **kwargs) -> None:
        """
        Log debug message.

        @brief Log debug message.
        @param message Message to log
        @param kwargs Additional log data
        """
        self.logger_manager.logger.debug(message, extra=kwargs)

    def connect_database(self) -> bool:
        """
        Connect to database.

        @brief Establish database connection.
        @return True if connection successful, False otherwise
        """
        try:
            if self.db_manager.connect():
                self.log_info("Database connected successfully")
                return True
            else:
                self.log_error("Database connection failed")
                return False
        except Exception as e:
            self.log_error(f"Database connection error: {str(e)}")
            return False

    def disconnect_database(self) -> None:
        """
        Disconnect from database.

        @brief Close database connection.
        """
        try:
            self.db_manager.disconnect()
            self.log_info("Database disconnected")
        except Exception as e:
            self.log_error(f"Database disconnection error: {str(e)}")

    def connect_messaging(self) -> bool:
        """
        Connect to messaging.

        @brief Establish messaging connection.
        @return True if connection successful, False otherwise
        """
        try:
            if self.mq_manager.connect():
                self.log_info("Messaging connected successfully")
                return True
            else:
                self.log_error("Messaging connection failed")
                return False
        except Exception as e:
            self.log_error(f"Messaging connection error: {str(e)}")
            return False

    def disconnect_messaging(self) -> None:
        """
        Disconnect from messaging.

        @brief Close messaging connection.
        """
        try:
            self.mq_manager.disconnect()
            self.log_info("Messaging disconnected")
        except Exception as e:
            self.log_error(f"Messaging disconnection error: {str(e)}")

    def execute_query(self, query: str, params: tuple | None = None) -> list:
        """
        Execute database query.

        @brief Execute SELECT query and return results.
        @param query SQL query string
        @param params Query parameters
        @return List of query results
        """
        try:
            results = self.db_manager.execute_query(query, params)
            self.log_info(f"Query executed successfully, {len(results)} rows returned")
            return results
        except Exception as e:
            self.log_error(f"Query execution failed: {str(e)}")
            raise

    def execute_update(self, query: str, params: tuple | None = None) -> int:
        """
        Execute database update.

        @brief Execute INSERT/UPDATE/DELETE query.
        @param query SQL query string
        @param params Query parameters
        @return Number of affected rows
        """
        try:
            rows_affected = self.db_manager.execute_update(query, params)
            self.log_info(f"Update executed successfully, {rows_affected} rows affected")
            return rows_affected
        except Exception as e:
            self.log_error(f"Update execution failed: {str(e)}")
            raise

    def send_message(
        self, queue_name: str, message: Any, properties: dict[str, Any] | None = None
    ) -> bool:
        """
        Send message to queue.

        @brief Send message to MQ queue.
        @param queue_name Name of the queue
        @param message Message content
        @param properties Message properties
        @return True if message sent successfully
        """
        try:
            success = self.mq_manager.put_message(queue_name, message, properties)
            if success:
                self.log_info(f"Message sent to queue {queue_name}")
            else:
                self.log_error(f"Failed to send message to queue {queue_name}")
            return success
        except Exception as e:
            self.log_error(f"Message sending failed: {str(e)}")
            return False

    def receive_message(self, queue_name: str, timeout: int | None = None) -> dict[str, Any] | None:
        """
        Receive message from queue.

        @brief Receive message from MQ queue.
        @param queue_name Name of the queue
        @param timeout Timeout in seconds
        @return Message data or None if no message
        """
        try:
            message = self.mq_manager.get_message(queue_name, timeout)
            if message:
                self.log_info(f"Message received from queue {queue_name}")
            return message
        except Exception as e:
            self.log_error(f"Message receiving failed: {str(e)}")
            return None

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the component.

        @brief Component-specific initialization logic.
        @return True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def run(self) -> bool:
        """
        Run the component.

        @brief Main component execution logic.
        @return True if execution successful, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Cleanup the component.

        @brief Component-specific cleanup logic.
        """
        pass

    def start(self) -> bool:
        """
        Start the component.

        @brief Complete component lifecycle: initialize, run, cleanup.
        @return True if component executed successfully, False otherwise
        """
        try:
            self.log_info(f"Starting component '{self.component_name}'")

            # Initialize component
            if not self.initialize():
                self.log_error("Component initialization failed")
                return False

            # Run component
            if not self.run():
                self.log_error("Component execution failed")
                return False

            self.log_info(f"Component '{self.component_name}' completed successfully")
            return True

        except Exception as e:
            self.log_error(f"Component execution error: {str(e)}")
            return False

        finally:
            # Always cleanup
            try:
                self.cleanup()
            except Exception as e:
                self.log_error(f"Component cleanup error: {str(e)}")
