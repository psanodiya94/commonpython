# CommonPython Framework

A comprehensive Python framework providing configuration management, logging, database connectivity, message queue operations, and command-line interface functionality using only standard Python modules and IBM CLI interfaces.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-130%20passed-brightgreen.svg)](scripts/test_commonpython.py)

## 🚀 Quick Start

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

# Or run the quick start script for guided setup
python examples/quick_start.py
```

## ✨ Features

- **🔧 Configuration Management**: YAML-based configuration with environment variable support
- **📝 Logging**: Human-readable and JSON logging with colored console output
- **🗄️ Database Operations**: IBM DB2 connectivity using CLI interface
- **📨 Message Queue**: IBM MQ operations using CLI interface
- **💻 Command Line Interface**: Full-featured CLI for all operations
- **🧩 Component Framework**: Common framework for building components with shared functionality
- **🧪 Testing**: Comprehensive test suite with coverage reporting
- **📚 Documentation**: Complete Doxygen-style documentation

## 📋 Requirements

- Python 3.8 or higher
- IBM DB2 CLI tools (for database operations)
- IBM MQ CLI tools (for messaging operations)
- Coverage (for testing only)

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
2. **🔧 Set Up Your Environment**: Install Python 3.8+ and IBM CLI tools
3. **📝 Use the Template**: Copy `examples/component_template.py` to start your first component
4. **⚙️ Configure**: Copy `config/config.yaml` and modify it for your environment
5. **🧪 Test**: Run the test suite to verify everything works
6. **🚀 Build**: Create your component using the framework's services

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

if __name__ == '__main__':
    sys.exit(0 if run_component(MyFirstComponent, "MyFirstComponent") else 1)
```

Run it:
```bash
python my_first_component.py --config config/config.yaml --verbose
```

## Installation

### Basic Installation

```bash
# Clone the repository
git clone <repository-url>
cd commonpython

# Install in development mode
pip install -e .

# Or install basic version
pip install -e . -f setup-basic.py
```

### Dependencies

The framework uses only standard Python modules with the following optional dependencies:

- `coverage>=7.0.0` (for testing only)

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
config_manager = ConfigManager('config.yaml')
logger_manager = LoggerManager('myapp', config_manager.get_logging_config())

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
if __name__ == '__main__':
    sys.exit(0 if run_component(MyComponent, "MyComponent") else 1)
```

**Run your component:**
```bash
python my_component.py --config config/component_config.yaml --verbose
```

## Testing

### Run Basic Tests

```bash
# Run basic test suite
python test_framework_basic.py

# Or use the test runner
python test/run_tests.py
```

### Run Comprehensive Tests

```bash
# Run comprehensive test suite
python test_framework.py

# Run with coverage
python test_framework.py --coverage
```

### Individual Test Modules

```bash
# Run specific test modules
python -m unittest test.test_config_manager
python -m unittest test.test_logger_manager
python -m unittest test.test_db2_manager
python -m unittest test.test_mq_manager
python -m unittest test.test_cli
```

## Architecture

### Module Structure

```text
commonpython/
├── commonpython/
│   ├── __init__.py              # Main package
│   ├── config/
│   │   ├── __init__.py          # Config module
│   │   └── config_manager.py   # Configuration management
│   ├── logging/
│   │   ├── __init__.py          # Logging module
│   │   └── logger_manager.py   # Logging functionality
│   ├── database/
│   │   ├── __init__.py          # Database module
│   │   └── db2_manager.py       # DB2 operations via CLI
│   ├── messaging/
│   │   ├── __init__.py          # Messaging module
│   │   └── mq_manager.py        # MQ operations via CLI
│   └── cli/
│       ├── __init__.py          # CLI module
│       └── cli.py               # Command-line interface
├── test/
│   ├── __init__.py              # Test package
│   ├── test_config_manager.py   # Configuration tests
│   ├── test_logger_manager.py   # Logging tests
│   ├── test_db2_manager.py      # Database tests
│   ├── test_mq_manager.py       # Messaging tests
│   ├── test_cli.py             # CLI tests
│   └── run_tests.py            # Test runner
├── config.yaml                 # Example configuration
├── requirements.txt            # Dependencies
├── setup.py                    # Setup script
├── test_framework.py          # Test framework
└── README.md                   # Documentation
```

### Key Design Principles

1. **Standard Library Only**: Uses only Python standard library modules
2. **CLI Interface**: Uses IBM CLI tools instead of SDK modules
3. **Comprehensive Testing**: Full test coverage with detailed reporting
4. **Documentation**: Complete Doxygen-style documentation
5. **Configuration**: Flexible configuration management
6. **Logging**: Structured logging with multiple output formats

## IBM CLI Requirements

### DB2 CLI Tools

The framework requires IBM DB2 CLI tools to be installed and available in the system PATH:

- `db2` command-line tool
- DB2 client libraries

### MQ CLI Tools

The framework requires IBM MQ CLI tools to be installed and available in the system PATH:

- `runmqsc` command-line tool
- `amqsput` and `amqsget` utilities
- MQ client libraries

## Development

### Adding New Features

1. Create new modules in appropriate directories
2. Add comprehensive test cases
3. Update CLI interface if needed
4. Update documentation
5. Ensure all tests pass

### Code Style

- Follow PEP 8 guidelines
- Use Doxygen-style documentation
- Write comprehensive test cases
- Maintain backward compatibility

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

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
2. **🧪 Run Tests**: Verify framework functionality with `python scripts/test_commonpython.py`
3. **📝 Check Logs**: Look for detailed error information in log files
4. **🔍 Review Examples**: Study the examples in the `examples/` directory
5. **🐛 Report Issues**: Create an issue with detailed information and logs

## 📚 Additional Resources

- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)**: Comprehensive guide for developers
- **[Examples](examples/)**: Working examples of components
- **[Templates](examples/)**: Component templates for quick start
- **[Test Suite](scripts/test_commonpython.py)**: Comprehensive test framework

## Support

For issues and questions:

1. Check the documentation and troubleshooting section above
2. Run the test suite to verify framework functionality
3. Review the examples and templates
4. Create an issue with detailed information and error logs
