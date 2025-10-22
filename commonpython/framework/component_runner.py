"""
Component Runner for CommonPython Framework

Provides a common way to run components with shared functionality.
"""

import argparse
from typing import Any

from .component_base import ComponentBase


class ComponentRunner:
    """
    Component runner for CommonPython framework.

    Provides a common way to run components with shared functionality
    including configuration, logging, database, and messaging capabilities.
    """

    def __init__(self, component_class: type[ComponentBase], component_name: str):
        """
        Initialize the component runner.

        @brief Initialize component runner with component class and name.
        @param component_class Component class that inherits from ComponentBase
        @param component_name Name of the component
        """
        self.component_class = component_class
        self.component_name = component_name
        self.component_instance = None

    def create_parser(self) -> argparse.ArgumentParser:
        """
        Create command-line argument parser.

        @brief Create argument parser for component execution.
        @return Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description=f"{self.component_name} - CommonPython Component",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            "--config", "-c", help="Configuration file path", default="config/config.yaml"
        )

        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set logging level",
            default="INFO",
        )

        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

        parser.add_argument(
            "--dry-run", action="store_true", help="Run in dry-run mode (no actual operations)"
        )

        return parser

    def run(self, args: list | None = None) -> bool:
        """
        Run the component.

        @brief Execute component with command-line arguments.
        @param args Command-line arguments (None to use sys.argv)
        @return True if component executed successfully, False otherwise
        """
        try:
            # Parse arguments
            parser = self.create_parser()
            parsed_args = parser.parse_args(args)

            # Create component instance
            self.component_instance = self.component_class(parsed_args.config)

            # Set log level if specified
            if parsed_args.log_level:
                self.component_instance.logger_manager.set_level(parsed_args.log_level)

            # Set verbose mode
            if parsed_args.verbose:
                self.component_instance.logger_manager.set_level("DEBUG")

            # Set dry-run mode
            if parsed_args.dry_run:
                self.component_instance.set_config("dry_run", True)
                self.component_instance.log_info("Running in dry-run mode")

            # Start component
            return self.component_instance.start()

        except KeyboardInterrupt:
            if self.component_instance:
                self.component_instance.log_info("Component interrupted by user")
            return False

        except Exception as e:
            if self.component_instance:
                self.component_instance.log_error(f"Component runner error: {str(e)}")
            else:
                print(f"Component runner error: {str(e)}")
            return False

    def run_with_config(self, config: dict[str, Any]) -> bool:
        """
        Run component with configuration dictionary.

        @brief Execute component with provided configuration.
        @param config Configuration dictionary
        @return True if component executed successfully, False otherwise
        """
        try:
            # Create component instance
            self.component_instance = self.component_class(
                None  # No config file, will use provided config
            )

            # Apply configuration
            for key, value in config.items():
                self.component_instance.set_config(key, value)

            # Start component
            return self.component_instance.start()

        except Exception as e:
            if self.component_instance:
                self.component_instance.log_error(f"Component runner error: {str(e)}")
            else:
                print(f"Component runner error: {str(e)}")
            return False


def run_component(
    component_class: type[ComponentBase], component_name: str, args: list | None = None
) -> bool:
    """
    Run a component with CommonPython framework.

    @brief Convenience function to run a component.
    @param component_class Component class that inherits from ComponentBase
    @param component_name Name of the component
    @param args Command-line arguments (None to use sys.argv)
    @return True if component executed successfully, False otherwise
    """
    runner = ComponentRunner(component_class, component_name)
    return runner.run(args)


def run_component_with_config(
    component_class: type[ComponentBase], component_name: str, config: dict[str, Any]
) -> bool:
    """
    Run a component with configuration dictionary.

    @brief Convenience function to run a component with config.
    @param component_class Component class that inherits from ComponentBase
    @param component_name Name of the component
    @param config Configuration dictionary
    @return True if component executed successfully, False otherwise
    """
    runner = ComponentRunner(component_class, component_name)
    return runner.run_with_config(config)
