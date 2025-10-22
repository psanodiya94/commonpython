# CommonPython Framework - Development Guide

This guide provides comprehensive information for developers who want to use the CommonPython framework to build components and tools.

## Table of Contents

1. [Quick Start](#quick-start)
1. [Framework Architecture](#framework-architecture)
1. [Creating Your First Component](#creating-your-first-component)
1. [Configuration Management](#configuration-management)
1. [Logging System](#logging-system)
1. [Database Operations](#database-operations)
1. [Messaging Operations](#messaging-operations)
1. [CLI Development](#cli-development)
1. [Testing Your Components](#testing-your-components)
1. [Best Practices](#best-practices)
1. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd commonpython

# Install in development mode
pip install -e .
```

### 2. Create Your First Component

```bash
# Copy the template
cp examples/component_template.py my_component.py

# Edit the template with your logic
# Run your component
python my_component.py --config config/config.yaml --verbose
```

### 3. Test the Framework

```bash
# Run all tests
python scripts/test_commonpython.py

# Run with coverage
python scripts/test_commonpython.py --coverage
```

## Framework Architecture

The CommonPython framework consists of several core modules:

### Core Modules

- **ConfigManager**: Centralized configuration management
- **LoggerManager**: Structured logging with multiple output formats
- **DB2Manager**: IBM DB2 database operations via CLI
- **MQManager**: IBM MQ messaging operations via CLI
- **CLI**: Command-line interface for all operations
- **ComponentBase**: Base class for building components
- **ComponentRunner**: Component lifecycle management
- **ComponentRegistry**: Component registration and discovery

### Design Principles

1. **Standard Library Only**: Uses only Python standard library modules
1. **CLI Interface**: Uses IBM CLI tools instead of SDK modules
1. **Configuration-Driven**: All behavior controlled by configuration
1. **Comprehensive Logging**: Structured logging with multiple formats
1. **Error Handling**: Built-in error handling and recovery
1. **Testing**: Comprehensive test coverage

## Creating Your First Component

### Step 1: Use the Template

Start with the provided template:

```python
from commonpython.framework import ComponentBase, run_component


class MyComponent(ComponentBase):
    def __init__(self, config_file=None):
        super().__init__("MyComponent", config_file)

    def initialize(self) -> bool:
        # Your initialization logic
        return True

    def run(self) -> bool:
        # Your main logic
        return True

    def cleanup(self) -> None:
        # Your cleanup logic
        pass


if __name__ == "__main__":
    sys.exit(0 if run_component(MyComponent, "MyComponent") else 1)
```

### Step 2: Implement Your Logic

```python
def run(self) -> bool:
    # Connect to services
    if self.connect_database():
        results = self.execute_query("SELECT * FROM my_table")
        self.log_info(f"Found {len(results)} records")

    if self.connect_messaging():
        self.send_message("MY.QUEUE", {"data": "message"})

    return True
```

### Step 3: Configure Your Component

Create a configuration file:

```yaml
# config/config.yaml
database:
  host: localhost
  port: 50000
  name: mydb
  user: myuser
  password: mypass

messaging:
  host: localhost
  port: 1414
  queue_manager: MY_QM
  channel: SYSTEM.DEF.SVRCONN

logging:
  level: INFO
  file: my_component.log
  json_format: false

component:
  # Your component-specific settings
  operation_count: 10
  delay_seconds: 2
```

## Configuration Management

### Configuration Sources

The framework supports multiple configuration sources with priority order:

1. **Environment Variables** (highest priority)
1. **Configuration Files**
1. **Default Values** (lowest priority)

### Environment Variables

Override any configuration using environment variables:

```bash
export DB2_HOST=my-db-server
export DB2_PORT=50000
export DB2_DATABASE=mydb
export DB2_USER=myuser
export DB2_PASSWORD=mypass

export MQ_HOST=my-mq-server
export MQ_PORT=1414
export MQ_QUEUE_MANAGER=MY_QM
export MQ_CHANNEL=SYSTEM.DEF.SVRCONN

export LOG_LEVEL=DEBUG
export LOG_FILE=my_component.log
```

### Configuration Access

```python
# Get configuration values
host = self.get_config("database.host", "localhost")
port = self.get_config("database.port", 50000)
operation_count = self.get_config("component.operation_count", 5)

# Set configuration values
self.set_config("component.custom_setting", "value")
```

## Logging System

### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about program execution
- **WARNING**: Something unexpected happened
- **ERROR**: A serious problem occurred
- **CRITICAL**: A very serious error occurred

### Logging Methods

```python
# Basic logging
self.log_info("Processing started")
self.log_warning("Connection timeout")
self.log_error("Database connection failed")
self.log_debug("Debug information")

# Structured logging
self.logger_manager.log_function_call("my_function", ("arg1",), {"key": "value"})
self.logger_manager.log_database_operation("SELECT", "users", "SELECT * FROM users")
self.logger_manager.log_mq_operation("PUT", "MY.QUEUE", {"data": "message"})
```

### Log Formats

The framework supports two log formats:

1. **Human-readable** (default):

   ```text
   2025-09-29 01:07:00,947 - MyComponent - INFO - Processing started
   ```

1. **JSON format**:

   ```json
   {"timestamp": "2025-09-29T01:07:00.947", "level": "INFO", "logger": "MyComponent", "message": "Processing started"}
   ```

## Database Operations

### Database Connection Management

```python
# Connect to database
if self.connect_database():
    self.log_info("Database connected")

    # Perform operations
    results = self.execute_query("SELECT * FROM users")

    # Disconnect
    self.disconnect_database()
else:
    self.log_error("Database connection failed")
```

### Query Operations

```python
# SELECT queries
results = self.execute_query("SELECT * FROM users WHERE active = ?", (True,))

# INSERT/UPDATE/DELETE operations
rows_affected = self.execute_update(
    "INSERT INTO users (name, email) VALUES (?, ?)", ("John Doe", "john@example.com")
)

# Batch operations
queries = [
    "INSERT INTO users (name) VALUES ('User 1')",
    "INSERT INTO users (name) VALUES ('User 2')",
]
self.execute_batch(queries)
```

### Transaction Management

```python
# Using context manager
with self.transaction():
    self.execute_update("INSERT INTO users (name) VALUES (?)", ("User 1",))
    self.execute_update("INSERT INTO users (name) VALUES (?)", ("User 2",))
    # Transaction is automatically committed
```

## Messaging Operations

### Messaging Connection Management

```python
# Connect to messaging
if self.connect_messaging():
    self.log_info("Messaging connected")

    # Perform operations
    self.send_message("MY.QUEUE", {"data": "message"})

    # Disconnect
    self.disconnect_messaging()
else:
    self.log_error("Messaging connection failed")
```

### Message Operations

```python
# Send messages
self.send_message("MY.QUEUE", {"data": "message"})
self.send_message("MY.QUEUE", "simple string message")
self.send_message("MY.QUEUE", b"binary data")

# Receive messages
message = self.receive_message("MY.QUEUE")
if message:
    self.log_info(f"Received: {message['data']}")

# Browse messages (peek without removing)
message = self.browse_message("MY.QUEUE")
```

### Queue Management

```python
# Get queue depth
depth = self.get_queue_depth("MY.QUEUE")
self.log_info(f"Queue depth: {depth}")

# Purge queue
self.purge_queue("MY.QUEUE")
```

## CLI Development

### Using the CLI

```bash
# Test database connection
commonpython database test

# Execute database query
commonpython database execute "SELECT * FROM users"

# Test messaging connection
commonpython messaging test

# Send message
commonpython messaging put MY.QUEUE "Hello World"

# Get message
commonpython messaging get MY.QUEUE

# Show configuration
commonpython config show

# Test all components
commonpython test-all
```

### Creating CLI Tools

```python
from commonpython.cli import CLI

# Initialize CLI
cli = CLI("config.yaml")

# Use CLI methods
cli.setup_database()
cli.execute_query("SELECT * FROM users")
cli.setup_messaging()
cli.put_message("MY.QUEUE", {"data": "message"})
```

## Testing Your Components

### Unit Testing

```python
import unittest
from unittest.mock import patch, MagicMock
from commonpython.framework import ComponentBase


class TestMyComponent(unittest.TestCase):
    def setUp(self):
        with patch("commonpython.framework.ComponentBase._initialize_services"):
            self.component = MyComponent()

    def test_initialize(self):
        result = self.component.initialize()
        self.assertTrue(result)

    def test_run(self):
        with patch.object(self.component, "connect_database", return_value=True):
            with patch.object(self.component, "execute_query", return_value=[]):
                result = self.component.run()
                self.assertTrue(result)
```

### Integration Testing

```python
# Test with actual configuration
component = MyComponent("test_config.yaml")
result = component.start()  # Runs initialize, run, cleanup
self.assertTrue(result)
```

### Running Tests

```bash
# Run all tests with coverage
python scripts/test_commonpython.py --cov

# Run specific test module
python -m unittest test.test_component_framework

# Run individual test case
python -m unittest test.test_cli.TestCLI.test_init
```

The test suite includes:

- 225+ comprehensive test cases
- 89% code coverage
- Thorough mocking of external dependencies
- Extensive edge case testing

Key test areas:

- Configuration management (YAML and environment variables)
- Logging system (console, file, JSON formats)
- Database operations (connection, queries, transactions)
- Message queue operations (send, receive, browse)
- Component lifecycle (initialize, run, cleanup)
- CLI functionality
- Error handling and recovery

## Best Practices

### 1. Configuration Management

- Use configuration files for all settings
- Provide sensible defaults
- Use environment variables for sensitive data
- Validate configuration on startup

### 2. Error Handling

```python
def run(self) -> bool:
    try:
        # Your logic here
        return True
    except DatabaseError as e:
        self.log_error(f"Database error: {str(e)}")
        return False
    except MessagingError as e:
        self.log_error(f"Messaging error: {str(e)}")
        return False
    except Exception as e:
        self.log_error(f"Unexpected error: {str(e)}")
        return False
```

### 3. Resource Management

```python
def cleanup(self) -> None:
    try:
        self.disconnect_database()
    except:
        pass

    try:
        self.disconnect_messaging()
    except:
        pass

    # Cleanup other resources
```

### 4. Logging

- Use appropriate log levels
- Include context in log messages
- Log errors with full exception information
- Use structured logging for complex data

### 5. Testing

- Write unit tests for all methods
- Test error conditions
- Use mocks for external dependencies
- Test configuration scenarios

## Troubleshooting

### Common Issues

#### 1. Configuration File Not Found

**Error**: `Configuration file 'config.yaml' not found`

**Solution**:

- Ensure the configuration file exists
- Check the file path
- Use absolute paths if needed

#### 2. Database Connection Failed

**Error**: `DB2 command error: [Errno 2] No such file or directory: 'db2'`

**Solution**:

- Install IBM DB2 CLI tools
- Add DB2 tools to system PATH
- Verify DB2 client installation

#### 3. Messaging Connection Failed

**Error**: `MQ command error: [Errno 2] No such file or directory: 'runmqsc'`

**Solution**:

- Install IBM MQ CLI tools
- Add MQ tools to system PATH
- Verify MQ client installation

#### 4. Permission Denied

**Error**: `Permission denied` when accessing log files

**Solution**:

- Check file permissions
- Ensure log directory exists
- Run with appropriate permissions

### Debug Mode

Enable debug logging for troubleshooting:

```yaml
logging:
  level: DEBUG
  console: true
```

Or use environment variable:

```bash
export LOG_LEVEL=DEBUG
```

### Getting Help

1. Check the logs for detailed error information
1. Run tests to verify framework functionality
1. Check configuration file syntax
1. Verify IBM CLI tools installation
1. Review the examples in the `examples/` directory

## Advanced Topics

### Custom Managers

You can extend the framework by creating custom managers:

```python
class CustomManager:
    def __init__(self, config, logger_manager):
        self.config = config
        self.logger = logger_manager.logger

    def custom_operation(self):
        self.logger.info("Custom operation executed")
```

### Component Registration

Register components for discovery:

```python
from commonpython.framework import register_component

register_component("MyComponent", MyComponent)

# Get registered component
component_class = get_component("MyComponent")
```

### Custom CLI Commands

Extend the CLI with custom commands:

```python
from commonpython.cli import CLI


class CustomCLI(CLI):
    def custom_command(self, args):
        # Your custom command logic
        pass
```

This development guide provides comprehensive information for using the CommonPython framework. For more examples, see the `examples/` directory and the test files in the `test/` directory.
