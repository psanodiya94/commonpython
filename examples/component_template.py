#!/usr/bin/env python3
"""
Component Template for CommonPython Framework

This template provides a starting point for creating new components using the CommonPython framework.
Copy this file and modify it according to your needs.

@brief Template for creating CommonPython components
@author Your Name
@version 1.0.0
"""

import sys
import time
from pathlib import Path

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.framework import ComponentBase, run_component


class MyComponent(ComponentBase):
    """
    My Component - Template for CommonPython Framework

    This is a template component that demonstrates how to use the CommonPython framework.
    Replace this class name and implementation with your own component logic.

    @brief Template component demonstrating CommonPython framework usage
    """

    def __init__(self, config_file: str = None):
        """
        Initialize the component.

        @brief Initialize component with configuration.
        @param config_file Path to configuration file (optional)
        """
        super().__init__("MyComponent", config_file)

    def initialize(self) -> bool:
        """
        Initialize the component.

        @brief Component-specific initialization logic.
        @return True if initialization successful, False otherwise
        """
        self.log_info("Initializing MyComponent")

        try:
            # Get component-specific configuration
            self.operation_count = self.get_config("component.operation_count", 5)
            self.delay_seconds = self.get_config("component.delay_seconds", 1)
            self.table_name = self.get_config("component.table_name", "my_table")
            self.queue_name = self.get_config("component.queue_name", "MY.QUEUE")

            self.log_info("Configuration loaded:")
            self.log_info(f"  - Operation count: {self.operation_count}")
            self.log_info(f"  - Delay seconds: {self.delay_seconds}")
            self.log_info(f"  - Table name: {self.table_name}")
            self.log_info(f"  - Queue name: {self.queue_name}")

            # Initialize any component-specific resources here
            # Example: Load data, connect to external services, etc.

            self.log_info("MyComponent initialization completed successfully")
            return True

        except Exception as e:
            self.log_error(f"MyComponent initialization failed: {str(e)}")
            return False

    def run(self) -> bool:
        """
        Run the component.

        @brief Main component execution logic.
        @return True if execution successful, False otherwise
        """
        self.log_info("Starting MyComponent execution")

        try:
            # Connect to services if needed
            db_connected = self.connect_database()
            mq_connected = self.connect_messaging()

            if db_connected:
                self.log_info("Database connection established")
            else:
                self.log_warning("Database connection failed - continuing without database")

            if mq_connected:
                self.log_info("Messaging connection established")
            else:
                self.log_warning("Messaging connection failed - continuing without messaging")

            # Perform main operations
            for i in range(self.operation_count):
                self.log_info(f"Performing operation {i + 1}/{self.operation_count}")

                try:
                    # Example: Database operations
                    if db_connected:
                        # Example query - replace with your actual queries
                        results = self.execute_query(f"SELECT COUNT(*) FROM {self.table_name}")
                        if results:
                            self.log_info(f"Table {self.table_name} has {results[0][0]} records")

                    # Example: Messaging operations
                    if mq_connected:
                        # Example message - replace with your actual messages
                        message_data = {
                            "operation_id": i + 1,
                            "timestamp": time.time(),
                            "data": f"Operation {i + 1} completed",
                        }
                        self.send_message(self.queue_name, message_data)
                        self.log_info(f"Message sent to {self.queue_name}")

                    # Simulate some work
                    time.sleep(self.delay_seconds)

                    self.log_info(f"Operation {i + 1} completed successfully")

                except Exception as e:
                    self.log_error(f"Operation {i + 1} failed: {str(e)}")
                    # Decide whether to continue or stop
                    # For this template, we'll continue with the next operation
                    continue

            # Disconnect from services
            if db_connected:
                self.disconnect_database()
                self.log_info("Database connection closed")

            if mq_connected:
                self.disconnect_messaging()
                self.log_info("Messaging connection closed")

            self.log_info("MyComponent execution completed successfully")
            return True

        except Exception as e:
            self.log_error(f"MyComponent execution failed: {str(e)}")
            return False

    def cleanup(self) -> None:
        """
        Cleanup the component.

        @brief Component-specific cleanup logic.
        """
        self.log_info("Cleaning up MyComponent")

        try:
            # Cleanup any component-specific resources here
            # Example: Close files, release locks, etc.

            # Ensure services are disconnected
            try:
                self.disconnect_database()
            except:
                pass

            try:
                self.disconnect_messaging()
            except:
                pass

            self.log_info("MyComponent cleanup completed")

        except Exception as e:
            self.log_error(f"MyComponent cleanup error: {str(e)}")


def main():
    """
    Main entry point for the component.

    @brief Run the component with command-line arguments.
    @return True if component executed successfully, False otherwise
    """
    return run_component(MyComponent, "MyComponent")


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
