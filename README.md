# CommonPython Framework

A comprehensive Python framework providing configuration management, logging, database connectivity, message queue operations, and command-line interface functionality. Features a **flexible adapter architecture** that supports both CLI-based and library-based implementations.

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-295%20passed-brightgreen.svg)](test/)
[![Coverage](https://img.shields.io/badge/coverage-89%25-green.svg)](test/)
[![Architecture](https://img.shields.io/badge/architecture-adapter%20pattern-blue.svg)](docs/ADAPTER_ARCHITECTURE.md)

## 🚀 Quick Start

### 1. Installation

#### Option A: Minimal Install (Mandatory Only)

```bash
# Clone the repository
git clone <repository-url>
cd commonpython

# Install core framework only
pip install -e .
```

#### Option B: High Performance (Recommended)

```bash
# Install with library adapters for 10-50x better performance
pip install -e ".[library]"
```

#### Option C: Full Development Setup

```bash
# Install everything (libraries + testing tools)
pip install -e ".[all]"
```

> 📖 **[Complete Installation Guide](docs/INSTALLATION.md)** - Detailed instructions for all scenarios

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

# Or run the quick start script for guided setup
python examples/quick_start.py
```

## ✨ Features

- **🔧 Configuration Management**: YAML-based configuration with environment variable support
- **📝 Logging**: Human-readable and JSON logging with colored console output
- **🗄️ Database Operations**: IBM DB2 connectivity with **both CLI and library implementations**
- **📨 Message Queue**: IBM MQ operations with **both CLI and library implementations**
- **🔄 Adapter Pattern**: Seamlessly switch between CLI and library implementations via configuration
- **💻 Command Line Interface**: Full-featured CLI for all operations
- **🧩 Component Framework**: Common framework for building components with shared functionality
- **🧪 Testing**: Comprehensive test suite with 295+ tests using Python's unittest framework
- **📚 Documentation**: Complete Doxygen-style documentation and architecture guides
- **🚀 Zero Migration Cost**: Switch implementations without changing application code

## 📋 Requirements

### ✅ Mandatory (Always Required)

| Requirement | Version | Purpose               | Install                                       |
| ----------- | ------- | --------------------- | --------------------------------------------- |
| **Python**  | 3.12+   | Core runtime          | [Download](https://www.python.org/downloads/) |
| **PyYAML**  | Latest  | Configuration parsing | `pip install pyyaml`                          |

### ⚙️ Optional - For CLI Implementation (Default)

| Requirement           | Purpose                      | Status                             |
| --------------------- | ---------------------------- | ---------------------------------- |
| **IBM DB2 CLI tools** | Database operations via CLI  | Optional - Only if using database  |
| **IBM MQ CLI tools**  | Messaging operations via CLI | Optional - Only if using messaging |

> 💡 **Note**: CLI implementation works without Python libraries but requires IBM CLI tools installed and in PATH.

### 🚀 Optional - For Library Implementation (Better Performance)

| Package    | Purpose               | Performance Gain | Install              |
| ---------- | --------------------- | ---------------- | -------------------- |
| **ibm_db** | Native DB2 operations | 10-50x faster    | `pip install ibm_db` |
| **pymqi**  | Native MQ operations  | 10-50x faster    | `pip install pymqi`  |

Install all library dependencies:

```bash
pip install ibm_db pymqi
```

> 💡 **Note**: Library implementations are **optional**. The framework automatically falls back to CLI if libraries aren't installed.

### 🧪 Optional - For Development & Testing

| Package      | Version | Purpose                | Install                |
| ------------ | ------- | ---------------------- | ---------------------- |
| **coverage** | 7.0.0+  | Code coverage analysis | `pip install coverage` |

______________________________________________________________________

**Compatibility Notes:**

- ✅ Framework tested with Python 3.12.3
- ⚠️ May work with Python 3.8+ (untested)
- 🔄 Auto-fallback: Library → CLI if dependencies missing

## 🏗️ Architecture: Adapter Pattern

**NEW!** The framework now features a flexible adapter architecture that allows you to switch between CLI-based and library-based implementations **without changing your code**.

### Why Use the Adapter Pattern?

✅ **Zero Code Changes**: Switch implementations via configuration
✅ **Better Performance**: Library adapters are 10-50x faster
✅ **Improved Security**: Native parameterized queries prevent SQL injection
✅ **Gradual Migration**: Migrate database and messaging independently
✅ **Auto-Fallback**: Automatically use CLI if libraries aren't installed

### Quick Example

```yaml
# config.yaml - Switch from CLI to library implementation
database:
  implementation: library  # Was: cli
  auto_fallback: true     # Fallback to CLI if library not available
  host: localhost
  # ... rest of config unchanged
```

**That's it!** No application code changes needed.

📚 **[Read the complete Adapter Architecture Guide](docs/ADAPTER_ARCHITECTURE.md)** for migration steps, performance comparisons, and best practices.

## 🎯 For New Users

### What is CommonPython Framework?

CommonPython is a framework that provides common functionality for building Python applications that need to interact with IBM DB2 databases and IBM MQ messaging systems. It's designed to:

- **Simplify Development**: Provides ready-to-use components for common tasks
- **Standardize Operations**: Ensures consistent configuration, logging, and error handling
- **Reduce Boilerplate**: Eliminates repetitive code for database and messaging operations
- **Enable Testing**: Built-in testing support with mocked services

### When to Use This Framework

Use CommonPython when you need to build applications that:

- Connect to IBM DB2 databases
- Send/receive messages via IBM MQ
- Require structured logging and configuration management
- Need consistent error handling and resource management
- Want to follow enterprise development patterns

### Getting Started as a New User

1. **📖 Read the Documentation**: Start with this README and the [Development Guide](docs/DEVELOPMENT_GUIDE.md)
1. **🔧 Set Up Your Environment**: Install Python 3.8+ and IBM CLI tools
1. **📝 Use the Template**: Copy `examples/component_template.py` to start your first component
1. **⚙️ Configure**: Copy `config/config.yaml` and modify it for your environment
1. **🧪 Test**: Run the test suite to verify everything works
1. **🚀 Build**: Create your component using the framework's services

**💡 Pro Tip**: Run `python examples/quick_start.py` for an interactive guided setup!

### Example: Your First Component

```python
from commonpython.framework import ComponentBase, run_component


class MyFirstComponent(ComponentBase):
    def __init__(self, config_file=None):
        super().__init__("MyFirstComponent", config_file)

    def initialize(self) -> bool:
        self.log_info("My first component is initializing!")
        return True

    def run(self) -> bool:
        self.log_info("My first component is running!")

        # Connect to database
        if self.connect_database():
            results = self.execute_query("SELECT COUNT(*) FROM users")
            self.log_info(f"Found {results[0][0]} users in database")

        # Send a message
        if self.connect_messaging():
            self.send_message("MY.QUEUE", {"message": "Hello from my component!"})

        return True

    def cleanup(self) -> None:
        self.log_info("My first component is cleaning up!")


if __name__ == "__main__":
    sys.exit(0 if run_component(MyFirstComponent, "MyFirstComponent") else 1)
```

Run it:

```bash
python my_first_component.py --config config/config.yaml --verbose
```

## Configuration

### Configuration File

The project includes an example configuration file `config/config.yaml`:

```yaml
database:
  host: localhost
  port: 50000
  name: testdb
  user: db2inst1
  password: password
  schema: myschema
  timeout: 30

messaging:
  host: localhost
  port: 1414
  queue_manager: QM1
  channel: SYSTEM.DEF.SVRCONN
  user: mquser
  password: mqpass
  timeout: 30

logging:
  level: INFO
  file: app.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  max_size: 10485760
  backup_count: 5
  colored: true
  json_format: false  # Set to true for JSON format
```

### Environment Variables

You can override configuration using environment variables:

```bash
export DB2_HOST=localhost
export DB2_PORT=50000
export DB2_DATABASE=testdb
export DB2_USER=db2inst1
export DB2_PASSWORD=password

export MQ_HOST=localhost
export MQ_PORT=1414
export MQ_QUEUE_MANAGER=QM1
export MQ_CHANNEL=SYSTEM.DEF.SVRCONN

export LOG_LEVEL=DEBUG
export LOG_FILE=app.log
```

## Usage

### Command Line Interface

The framework provides a comprehensive CLI for all operations:

```bash
# Test database connection
commonpython database test

# Execute database query
commonpython database execute "SELECT * FROM users"

# Test MQ connection
commonpython messaging test

# Get message from queue
commonpython messaging get TEST.QUEUE

# Put message to queue
commonpython messaging put TEST.QUEUE "Hello World"

# Show configuration
commonpython config show

# Test all components
commonpython test-all
```

### Programmatic Usage

```python
from commonpython.config import ConfigManager
from commonpython.logging import LoggerManager
from commonpython.database import DB2Manager
from commonpython.messaging import MQManager

# Initialize configuration
config_manager = ConfigManager("config.yaml")
logger_manager = LoggerManager("myapp", config_manager.get_logging_config())

# Database operations
db_config = config_manager.get_database_config()
db_manager = DB2Manager(db_config, logger_manager)

if db_manager.connect():
    results = db_manager.execute_query("SELECT * FROM users")
    print(f"Found {len(results)} users")
    db_manager.disconnect()

# Message queue operations
mq_config = config_manager.get_messaging_config()
mq_manager = MQManager(mq_config, logger_manager)

if mq_manager.connect():
    mq_manager.put_message("TEST.QUEUE", {"message": "Hello World"})
    message = mq_manager.get_message("TEST.QUEUE")
    if message:
        print(f"Received: {message['data']}")
    mq_manager.disconnect()
```

### Component Framework Usage

Create components that use the framework's shared functionality:

```python
from commonpython.framework import ComponentBase, run_component


class MyComponent(ComponentBase):
    def __init__(self, config_file=None):
        super().__init__("MyComponent", config_file)

    def initialize(self) -> bool:
        # Your initialization logic
        self.log_info("Component initialized")
        return True

    def run(self) -> bool:
        # Your main logic
        if self.connect_database():
            results = self.execute_query("SELECT * FROM my_table")
            self.log_info(f"Found {len(results)} records")

        if self.connect_messaging():
            self.send_message("MY.QUEUE", {"data": "message"})

        return True

    def cleanup(self) -> None:
        # Your cleanup logic
        self.log_info("Component cleanup completed")


# Run the component
if __name__ == "__main__":
    sys.exit(0 if run_component(MyComponent, "MyComponent") else 1)
```

**Run your component:**

```bash
python my_component.py --config config/component_config.yaml --verbose
```

## Testing

The framework uses Python's built-in **unittest** framework (no third-party test frameworks required).

### Run All Tests

```bash
# Run all tests
python -m unittest discover -s test -p "test_*.py" -v

# Or use the test script
python scripts/test_commonpython.py
```

### Run Tests with Coverage

```bash
# Install coverage (optional)
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s test -p "test_*.py" -v
coverage report -m
coverage html  # Generate HTML report in htmlcov/
```

### Run Individual Test Modules

```bash
# Run specific test modules
python -m unittest test.test_config_manager -v
python -m unittest test.test_logger_manager -v
python -m unittest test.test_db2_manager -v
python -m unittest test.test_mq_manager -v
python -m unittest test.test_cli -v
```

### Test Structure

All tests use Python's standard `unittest` framework:

- No pytest or other third-party test frameworks
- All test files follow the pattern `test_*.py`
- Tests can be run individually or as a complete suite
- Coverage reporting uses the `coverage` package

## Architecture

### Repository Structure

```text
commonpython/
├── commonpython/               # Main package
│   ├── adapters/              # Adapter pattern implementations
│   ├── cli/                   # Command-line interface
│   ├── config/                # Configuration management
│   ├── database/              # Database operations
│   ├── factories/             # Factory pattern for adapters
│   ├── framework/             # Component framework
│   ├── interfaces/            # Abstract interfaces
│   ├── logging/               # Logging functionality
│   └── messaging/             # Message queue operations
├── config/                    # Configuration examples
│   ├── config.yaml           # Main config example
│   └── component_config.yaml # Component config example
├── docs/                      # Documentation
│   ├── ADAPTER_ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── CONTRIBUTING.md
│   ├── DEVELOPMENT_GUIDE.md
│   ├── Doxyfile              # Doxygen configuration
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── IMPROVEMENTS.md
│   └── INSTALLATION.md
├── examples/                  # Example code
│   ├── component_template.py
│   └── quick_start.py
├── scripts/                   # Utility scripts
│   └── test_commonpython.py  # Test runner
├── test/                      # Test suite (unittest)
│   ├── test_*.py             # Test modules
│   └── __init__.py
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
├── pyproject.toml            # Project metadata (modern)
├── README.md                 # This file
├── requirements.txt          # Test dependencies
└── setup.py                  # Setup script (legacy compat)
```

### Key Design Principles

1. **Minimal Dependencies**: Only PyYAML required; everything else is optional
1. **Adapter Pattern**: Switch between CLI and library implementations seamlessly
1. **unittest Framework**: All tests use Python's built-in unittest (no pytest)
1. **Comprehensive Testing**: Full test coverage with unittest and coverage reporting
1. **Complete Documentation**: Doxygen-style docs and architecture guides in docs/
1. **Flexible Configuration**: YAML-based with environment variable support
1. **Structured Logging**: Multiple output formats (console, JSON, colored)

## Development

### Adding New Features

1. Create new modules in appropriate directories
1. Add comprehensive test cases
1. Update CLI interface if needed
1. Update documentation
1. Ensure all tests pass

### Code Style

- Follow PEP 8 guidelines
- Use Doxygen-style documentation
- Write comprehensive test cases
- Maintain backward compatibility

## License

MIT License - see LICENSE file for details.

______________________________________________________________________

> **Note:** This tool was developed with the assistance of AI tools including Claude by Anthropic.

## Contributing

1. Fork the repository
1. Create a feature branch
1. Make your changes
1. Add tests for new functionality
1. Ensure all tests pass
1. Submit a pull request

## 🔧 Troubleshooting

### Common Issues

#### Configuration File Not Found

**Error**: `Configuration file 'config.yaml' not found`
**Solution**:

- Copy `config.yaml` to your project directory
- Use absolute paths: `--config /path/to/config.yaml`
- Check file permissions

#### Database Connection Failed

**Error**: `DB2 command error: [Errno 2] No such file or directory: 'db2'`
**Solution**:

- Install IBM DB2 CLI tools
- Add DB2 tools to system PATH: `export PATH=$PATH:/opt/ibm/db2/V11.5/bin`
- Verify installation: `db2 -v`

#### Messaging Connection Failed

**Error**: `MQ command error: [Errno 2] No such file or directory: 'runmqsc'`
**Solution**:

- Install IBM MQ CLI tools
- Add MQ tools to system PATH: `export PATH=$PATH:/opt/mqm/bin`
- Verify installation: `runmqsc -v`

#### Permission Denied

**Error**: `Permission denied` when accessing log files
**Solution**:

- Check file permissions: `chmod 755 log/`
- Ensure log directory exists: `mkdir -p log`
- Run with appropriate permissions

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Using environment variable
export LOG_LEVEL=DEBUG
python my_component.py

# Using configuration file
logging:
  level: DEBUG
  console: true
```

### Getting Help

1. **📚 Check Documentation**: Read this README and [Development Guide](docs/DEVELOPMENT_GUIDE.md)
1. **🧪 Run Tests**: Verify framework functionality with `python scripts/test_commonpython.py`
1. **📝 Check Logs**: Look for detailed error information in log files
1. **🔍 Review Examples**: Study the examples in the `examples/` directory
1. **🐛 Report Issues**: Create an issue with detailed information and logs

## 📚 Additional Resources

- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)**: Comprehensive guide for developers
- **[Adapter Architecture](docs/ADAPTER_ARCHITECTURE.md)**: Migration guide and design details
- **[Installation Guide](docs/INSTALLATION.md)**: Detailed installation instructions
- **[Changelog](docs/CHANGELOG.md)**: Version history and changes
- **[Contributing](docs/CONTRIBUTING.md)**: How to contribute to the project
- **[Examples](examples/)**: Working examples of components
- **[Test Suite](scripts/test_commonpython.py)**: Comprehensive unittest-based test framework

## Support

For issues and questions:

1. Check the documentation and troubleshooting section above
1. Run the test suite to verify framework functionality
1. Review the examples and templates
1. Create an issue with detailed information and error logs
