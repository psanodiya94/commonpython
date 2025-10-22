# Adapter Architecture Guide

## Overview

The CommonPython framework uses an **Adapter Pattern** architecture that allows seamless switching between CLI-based and library-based implementations for database and messaging operations. This design provides maximum flexibility while maintaining backward compatibility.

## Architecture Components

### 1. Interfaces (Abstract Base Classes)

Located in `commonpython/interfaces/`, these define the contracts that all implementations must follow:

- **`IDatabaseManager`**: Abstract interface for database operations
- **`IMessagingManager`**: Abstract interface for messaging operations

All database and messaging adapters implement these interfaces, ensuring consistent behavior regardless of the underlying implementation.

### 2. Adapters

Located in `commonpython/adapters/`, these wrap concrete implementations:

#### CLI Adapters (Always Available)

- **`DB2CLIAdapter`**: Wraps the existing CLI-based `DB2Manager`
- **`MQCLIAdapter`**: Wraps the existing CLI-based `MQManager`

#### Library Adapters (Optional - require additional dependencies)

- **`DB2LibraryAdapter`**: Uses `ibm_db` Python library for direct DB2 access
- **`MQLibraryAdapter`**: Uses `pymqi` Python library for direct MQ access

### 3. Factory Pattern

Located in `commonpython/factories/manager_factory.py`:

- **`ManagerFactory`**: Creates manager instances based on configuration
- Automatically detects available implementations
- Supports auto-fallback when library dependencies aren't installed
- Caches adapter availability for performance

## Benefits of This Architecture

### 1. **Zero Code Changes for Migration**

Switch from CLI to library implementation by changing a single configuration value:

```yaml
# Before (CLI):
database:
  implementation: cli
  host: localhost
  # ... other settings

# After (Library):
database:
  implementation: library
  host: localhost
  # ... other settings
```

**No changes needed** in your application code!

### 2. **Gradual Migration**

Migrate one service at a time:

```yaml
database:
  implementation: library  # Use library for database

messaging:
  implementation: cli      # Keep CLI for messaging
```

### 3. **Automatic Fallback**

If library dependencies aren't installed, automatically fallback to CLI:

```yaml
database:
  implementation: library
  auto_fallback: true  # Falls back to CLI if ibm_db not installed
```

### 4. **Better Performance**

Library implementations provide:

- ✅ Connection pooling
- ✅ Prepared statements
- ✅ Proper parameterized queries (prevents SQL injection)
- ✅ Native database features
- ✅ Lower overhead (no subprocess calls)

### 5. **Improved Security**

```python
# CLI Adapter - Limited parameterization
results = db_manager.execute_query("SELECT * FROM users WHERE id = 123")

# Library Adapter - Full parameterization support
results = db_manager.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
```

### 6. **Easier Testing**

Mock interfaces instead of subprocess calls:

```python
# Easy to mock
mock_db = Mock(spec=IDatabaseManager)
mock_db.execute_query.return_value = [{"id": 1, "name": "test"}]

# Use in tests
component.db_manager = mock_db
```

## Configuration Guide

### Database Configuration

```yaml
database:
  # Implementation type: 'cli' (default) or 'library' (requires ibm_db)
  implementation: cli

  # Auto fallback to CLI if library is not available (default: true)
  auto_fallback: true

  # Connection details
  host: localhost
  port: 50000
  name: testdb
  user: db2inst1
  password: password
  schema: myschema
  timeout: 30
```

### Messaging Configuration

```yaml
messaging:
  # Implementation type: 'cli' (default) or 'library' (requires pymqi)
  implementation: cli

  # Auto fallback to CLI if library is not available (default: true)
  auto_fallback: true

  # Connection details
  host: localhost
  port: 1414
  queue_manager: QM1
  channel: SYSTEM.DEF.SVRCONN
  user: mquser
  password: mqpass
  timeout: 30
```

## Migration Guide

### Step 1: Install Library Dependencies (Optional)

For DB2 library support:

```bash
pip install ibm_db
```

For MQ library support:

```bash
pip install pymqi
```

### Step 2: Update Configuration

Modify your `config.yaml`:

```yaml
database:
  implementation: library
  auto_fallback: true  # Recommended for safety
  # ... rest of config
```

### Step 3: Test Your Application

Run your application and verify:

1. Check logs for adapter selection messages
1. Verify functionality works as expected
1. Monitor performance improvements

### Step 4: Disable Auto-Fallback (Production)

Once verified, disable auto-fallback for stricter validation:

```yaml
database:
  implementation: library
  auto_fallback: false  # Fail fast if library not available
```

## Checking Available Implementations

Programmatically check which implementations are available:

```python
from commonpython.factories import ManagerFactory

available = ManagerFactory.get_available_implementations()

print("Database implementations:")
print(f"  CLI: {available['database']['cli']}")
print(f"  Library: {available['database']['library']}")

print("Messaging implementations:")
print(f"  CLI: {available['messaging']['cli']}")
print(f"  Library: {available['messaging']['library']}")
```

## Code Examples

### Using in Components

Components automatically use the factory pattern - no code changes needed:

```python
from commonpython.framework import ComponentBase, run_component


class MyComponent(ComponentBase):
    def __init__(self, config_file=None):
        super().__init__("MyComponent", config_file)

    def initialize(self) -> bool:
        self.log_info("Component initialized")
        return True

    def run(self) -> bool:
        # Works with both CLI and library implementations!
        if self.connect_database():
            results = self.execute_query("SELECT * FROM users WHERE id = ?", (123,))
            self.log_info(f"Found {len(results)} users")

        if self.connect_messaging():
            self.send_message("MY.QUEUE", {"data": "message"})

        return True

    def cleanup(self) -> None:
        self.log_info("Component cleanup completed")


if __name__ == "__main__":
    sys.exit(0 if run_component(MyComponent, "MyComponent") else 1)
```

### Direct Usage

```python
from commonpython.factories import ManagerFactory
from commonpython.config import ConfigManager
from commonpython.logging import LoggerManager

# Load configuration
config_manager = ConfigManager("config.yaml")
logger_manager = LoggerManager("myapp", config_manager.get_logging_config())

# Create managers using factory
db_config = config_manager.get_database_config()
db_manager = ManagerFactory.create_database_manager(db_config, logger_manager)

mq_config = config_manager.get_messaging_config()
mq_manager = ManagerFactory.create_messaging_manager(mq_config, logger_manager)

# Use managers - interface is identical regardless of implementation!
if db_manager.connect():
    results = db_manager.execute_query("SELECT * FROM users")
    db_manager.disconnect()

if mq_manager.connect():
    mq_manager.put_message("TEST.QUEUE", {"message": "Hello"})
    mq_manager.disconnect()
```

## Performance Comparison

| Operation           | CLI Implementation | Library Implementation |
| ------------------- | ------------------ | ---------------------- |
| Connect             | ~500ms             | ~100ms                 |
| Simple Query        | ~200ms             | ~10ms                  |
| Parameterized Query | Limited support    | Full support (safe)    |
| Transaction         | Manual via CLI     | Native support         |
| Connection Pooling  | ❌ Not supported   | ✅ Supported           |
| Prepared Statements | ❌ Not supported   | ✅ Supported           |

## Troubleshooting

### Library Not Loading

**Problem**: Configuration specifies `library` but CLI is being used.

**Solution**: Check that dependencies are installed:

```bash
pip install ibm_db pymqi
```

Check logs for fallback warnings:

```
WARNING - DB2 library adapter not available (ibm_db not installed), falling back to CLI adapter
```

### Import Errors

**Problem**: `ImportError` when using library implementation.

**Solution**:

1. Ensure dependencies are installed
1. Enable auto_fallback in config:
   ```yaml
   database:
     implementation: library
     auto_fallback: true
   ```

### Connection Failures

**Problem**: Connections fail with library implementation but work with CLI.

**Solution**:

1. Verify connection parameters are identical
1. Check library-specific requirements (e.g., SSL certificates)
1. Review library documentation for additional configuration

## Best Practices

1. **Use Auto-Fallback in Development**: Enable `auto_fallback: true` during development
1. **Disable in Production**: Set `auto_fallback: false` in production for explicit control
1. **Test Both Implementations**: Verify functionality with both CLI and library adapters
1. **Monitor Logs**: Check logs for adapter selection and warnings
1. **Gradual Rollout**: Migrate one service at a time (database first, then messaging)
1. **Use Parameterized Queries**: Always use parameters with library adapters for security

## Future Enhancements

The adapter architecture supports easy addition of new implementations:

- SQLAlchemy adapter for database operations
- Different messaging brokers (RabbitMQ, Kafka)
- Cloud-native services (AWS RDS, Azure Service Bus)
- Mock adapters for testing

Simply implement the interface and register with the factory!
