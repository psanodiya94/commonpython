#!/usr/bin/env python3
"""
CommonPython Framework - Quick Start Script

This script helps new users get started with the CommonPython framework by:
1. Testing the framework installation
2. Creating a sample component
3. Running a basic test

@brief Quick start script for new users
@author CommonPython Framework Team
@version 2.0.0
"""

import os
import sys
from pathlib import Path


def test_framework_installation():
    """
    Test if the framework is properly installed.

    @brief Test framework installation and imports.
    @return True if installation is successful, False otherwise
    """
    print("🔍 Testing framework installation...")

    try:
        # Test imports
        from commonpython.config import ConfigManager
        from commonpython.database import DB2Manager  # noqa: F401
        from commonpython.framework import ComponentBase, run_component  # noqa: F401
        from commonpython.logging import LoggerManager
        from commonpython.messaging import MQManager  # noqa: F401

        print("✅ All imports successful!")

        # Test basic functionality
        config_manager = ConfigManager()
        logging_config = config_manager.get_logging_config()
        logger_manager = LoggerManager("QuickStartTest", logging_config)

        logger_manager.logger.info("Framework installation test completed successfully")
        print("✅ Basic functionality test successful!")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you've installed the framework: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ Framework test failed: {e}")
        return False


def create_sample_component():
    """
    Create a sample component for testing.

    @brief Create a sample component to demonstrate framework usage.
    @return Path to the created component file
    """
    print("📝 Creating sample component...")

    sample_component_code = '''#!/usr/bin/env python3
"""
Sample Component for CommonPython Framework

This is a sample component created by the quick start script.
It demonstrates basic framework usage.
"""

import sys
from pathlib import Path

# Add the parent directory to the path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from commonpython.framework import ComponentBase, run_component


class SampleComponent(ComponentBase):
    """
    Sample component demonstrating CommonPython framework usage.
    """

    def __init__(self, config_file=None):
        super().__init__("SampleComponent", config_file)

    def initialize(self) -> bool:
        self.log_info("Sample component is initializing!")

        # Get some configuration
        operation_count = self.get_config('component.operation_count', 3)
        self.log_info(f"Will perform {operation_count} operations")

        return True

    def run(self) -> bool:
        self.log_info("Sample component is running!")

        # Try to connect to services (will fail gracefully if not available)
        db_connected = self.connect_database()
        mq_connected = self.connect_messaging()

        if db_connected:
            self.log_info("✅ Database connection successful!")
        else:
            self.log_info("ℹ️  Database connection failed (expected if DB2 not available)")

        if mq_connected:
            self.log_info("✅ Messaging connection successful!")
        else:
            self.log_info("ℹ️  Messaging connection failed (expected if MQ not available)")

        # Perform some sample operations
        operation_count = self.get_config('component.operation_count', 3)
        for i in range(operation_count):
            self.log_info(f"Performing sample operation {i + 1}/{operation_count}")

        self.log_info("Sample component execution completed successfully!")
        return True

    def cleanup(self) -> None:
        self.log_info("Sample component is cleaning up!")

        # Ensure services are disconnected
        try:
            self.disconnect_database()
        except:
            pass

        try:
            self.disconnect_messaging()
        except:
            pass


def main():
    return run_component(SampleComponent, "SampleComponent")


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
'''

    # Create the sample component file
    sample_file = Path("sample_component.py")
    with open(sample_file, "w") as f:
        f.write(sample_component_code)

    print(f"✅ Sample component created: {sample_file}")
    return str(sample_file)


def create_sample_config():
    """
    Create a sample configuration file.

    @brief Create a sample configuration file for testing.
    @return Path to the created configuration file
    """
    print("⚙️  Creating sample configuration...")

    sample_config = """# Sample Configuration for CommonPython Framework
# This configuration file is created by the quick start script

# Database configuration (will fail gracefully if DB2 not available)
database:
  host: localhost
  port: 50000
  name: sampledb
  user: sampleuser
  password: samplepass
  schema: sampleschema
  timeout: 30

# Messaging configuration (will fail gracefully if MQ not available)
messaging:
  host: localhost
  port: 1414
  queue_manager: SAMPLE_QM
  channel: SYSTEM.DEF.SVRCONN
  user: sampleuser
  password: samplepass
  timeout: 30

# Logging configuration
logging:
  level: INFO
  file: sample_component.log
  dir: log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  max_size: 10485760
  backup_count: 5
  colored: true
  json_format: false
  console: true

# Component-specific configuration
component:
  operation_count: 3
  delay_seconds: 1
"""

    # Create the sample configuration file
    config_file = Path("sample_config.yaml")
    with open(config_file, "w") as f:
        f.write(sample_config)

    print(f"✅ Sample configuration created: {config_file}")
    return str(config_file)


def run_sample_component(component_file, config_file):
    """
    Run the sample component.

    @brief Run the sample component to demonstrate framework usage.
    @param component_file Path to the component file
    @param config_file Path to the configuration file
    @return True if component ran successfully, False otherwise
    """
    print("🚀 Running sample component...")

    try:
        # Import and run the component
        import importlib.util

        spec = importlib.util.spec_from_file_location("sample_component", component_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Create a component instance with the config file
        component = module.SampleComponent(config_file)

        # Run the component
        result = component.start()

        if result:
            print("✅ Sample component ran successfully!")
            return True
        else:
            print("❌ Sample component failed!")
            return False

    except Exception as e:
        print(f"❌ Error running sample component: {e}")
        return False


def cleanup_files(files):
    """
    Clean up temporary files.

    @brief Remove temporary files created during quick start.
    @param files List of file paths to remove
    """
    print("🧹 Cleaning up temporary files...")

    for file_path in files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
        except Exception as e:
            print(f"⚠️  Could not remove {file_path}: {e}")


def main():
    """
    Main quick start function.

    @brief Run the complete quick start process.
    """
    print("🎉 Welcome to CommonPython Framework Quick Start!")
    print("=" * 60)

    # Test framework installation
    if not test_framework_installation():
        print("\n❌ Framework installation test failed!")
        print("💡 Please check your installation and try again.")
        return False

    print("\n" + "=" * 60)

    # Create sample files
    component_file = create_sample_component()
    config_file = create_sample_config()

    print("\n" + "=" * 60)

    # Run sample component
    success = run_sample_component(component_file, config_file)

    print("\n" + "=" * 60)

    # Ask user if they want to keep the sample files
    keep_files = input("\n🤔 Would you like to keep the sample files? (y/n): ").lower().strip()

    if keep_files in ["y", "yes"]:
        print("✅ Sample files kept:")
        print(f"   - Component: {component_file}")
        print(f"   - Configuration: {config_file}")
        print("\n💡 You can now modify these files to create your own components!")
    else:
        cleanup_files([component_file, config_file])

    print("\n" + "=" * 60)

    if success:
        print("🎉 Quick start completed successfully!")
        print("\n📚 Next steps:")
        print("1. Read the README.md for detailed documentation")
        print("2. Check out the examples/ directory for more examples")
        print("3. Use templates/component_template.py as a starting point")
        print("4. Read docs/DEVELOPMENT_GUIDE.md for comprehensive guidance")
        print("\n🚀 Happy coding with CommonPython Framework!")
    else:
        print("❌ Quick start encountered some issues.")
        print(
            "💡 Check the error messages above and refer to the troubleshooting section in README.md"
        )

    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
