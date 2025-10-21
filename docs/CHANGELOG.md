# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern Python packaging with `pyproject.toml` (PEP 517/518)
- Pre-commit hooks configuration for automated code quality checks
- Comprehensive `CONTRIBUTING.md` guide for contributors
- `CHANGELOG.md` for tracking version changes
- GitHub Actions CI/CD workflows for automated testing
- Custom exceptions module for better error handling
- Development dependencies: pytest, black, ruff, mypy
- MIT `LICENSE` file
- Enhanced development tooling configuration

### Changed
- Migrated from `setup.py` to `pyproject.toml` for modern packaging
- Improved error messages with more context
- Updated documentation with contribution guidelines

### Security
- Added bandit security scanning in pre-commit hooks
- Added private key detection in pre-commit hooks

## [2.0.0] - 2024-10-21

### Added
- **Adapter Pattern Architecture**: Seamless switching between CLI and library implementations
- Database adapters: `DB2CLIAdapter` and `DB2LibraryAdapter`
- Messaging adapters: `MQCLIAdapter` and `MQLibraryAdapter`
- Interfaces: `IDatabaseManager` and `IMessagingManager`
- Factory pattern: `ManagerFactory` for creating manager instances
- Auto-fallback mechanism when library dependencies aren't available
- 70 new test cases for adapters, factory, and integration
- Comprehensive adapter architecture documentation
- Enhanced test runner with categorization and metrics
- Implementation summary document
- Installation guide with dependency clarification

### Changed
- `ComponentBase` now uses factory pattern for manager creation
- Enhanced test suite organization with 9 categories
- Improved documentation structure
- Updated README with adapter pattern information
- Clarified mandatory vs optional dependencies

### Performance
- Library adapters provide 10-50x performance improvement
- Connection pooling support in library adapters
- Native prepared statements and parameterized queries

### Security
- Parameterized queries in library adapters prevent SQL injection
- Proper input validation and sanitization

### Fixed
- Various bug fixes and stability improvements

## [1.0.0] - 2024-10-15

### Added
- Initial release of CommonPython Framework
- Configuration management with YAML support
- Logging with colored console output and JSON format
- IBM DB2 database operations via CLI
- IBM MQ messaging operations via CLI
- Command-line interface for all operations
- Component framework for building applications
- Comprehensive test suite with 225 test cases
- Complete Doxygen-style documentation
- Example components and templates

### Features
- YAML-based configuration with environment variable support
- Human-readable and JSON logging
- DB2 connectivity using CLI tools
- MQ operations using CLI tools
- Full-featured CLI for database and messaging operations
- Component base class with shared functionality
- Comprehensive test coverage

### Documentation
- Complete README with usage examples
- Development guide
- Configuration examples
- Component templates

---

## Version History Summary

- **2.0.0**: Adapter pattern architecture, library support, enhanced testing
- **1.0.0**: Initial release with CLI-based implementations

## Migration Guides

### Migrating to 2.0.0

The 2.0.0 release maintains full backward compatibility. To take advantage of new library adapters:

1. **Install library dependencies** (optional):
   ```bash
   pip install -e ".[library]"
   ```

2. **Update configuration** to use library implementation:
   ```yaml
   database:
     implementation: library  # or keep 'cli'
     auto_fallback: true
   ```

3. **No code changes required** - existing code continues to work

See [docs/ADAPTER_ARCHITECTURE.md](docs/ADAPTER_ARCHITECTURE.md) for detailed migration guide.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to this project.

## Links

- [Homepage](https://github.com/psanodiya94/commonpython)
- [Issues](https://github.com/psanodiya94/commonpython/issues)
- [Pull Requests](https://github.com/psanodiya94/commonpython/pulls)
