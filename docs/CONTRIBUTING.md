# Contributing to CommonPython Framework

Thank you for your interest in contributing to CommonPython! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal or political attacks
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of IBM DB2 and IBM MQ (for relevant contributions)

### Finding Ways to Contribute

1. **Bug Reports**: Check the [Issues](https://github.com/psanodiya94/commonpython/issues) page
2. **Feature Requests**: Propose new features by opening an issue
3. **Documentation**: Improve or add documentation
4. **Code**: Fix bugs or implement features

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/commonpython.git
cd commonpython

# Add upstream remote
git remote add upstream https://github.com/psanodiya94/commonpython.git
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
# Install the package in development mode with all dependencies
pip install -e ".[all]"

# Or just development dependencies
pip install -e ".[dev]"
```

### 4. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files (optional)
pre-commit run --all-files
```

### 5. Verify Setup

```bash
# Run tests to verify everything works
python scripts/test_commonpython.py

# Or using pytest
pytest

# Check code formatting
black --check .
ruff check .
mypy commonpython/
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Make sure you're on main and up to date
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write code following the [Coding Standards](#coding-standards)
- Add or update tests as needed
- Update documentation if applicable
- Ensure pre-commit hooks pass

### 3. Test Your Changes

```bash
# Run all tests
python scripts/test_commonpython.py

# Run specific test module
python -m pytest test/test_config_manager.py

# Run with coverage
python scripts/test_commonpython.py --coverage

# Check code formatting
black .
ruff check . --fix
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new feature X"

# Pre-commit hooks will run automatically
```

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**

```bash
git commit -m "feat(database): add connection pooling support"
git commit -m "fix(logging): correct JSON format output"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(adapters): add integration tests for library adapters"
```

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create a pull request on GitHub
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 100 characters (enforced by Black)
- **Quotes**: Double quotes for strings (enforced by Black)
- **Type hints**: Required for all public functions and methods
- **Docstrings**: Required for all modules, classes, and public methods

### Code Formatting

We use automated tools for code formatting:

- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **MyPy**: Type checking

```bash
# Format code with black
black .

# Check and fix linting issues
ruff check . --fix

# Type checking
mypy commonpython/
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ConfigManager`)
- **Functions/Methods**: `snake_case` (e.g., `get_config_value`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- **Private methods**: `_leading_underscore` (e.g., `_internal_method`)

### Documentation Style

We use Doxygen-style docstrings:

```python
def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return results.

    @brief Execute SELECT query with optional parameters.
    @param query SQL query string (use ? for parameters)
    @param params Query parameters tuple (optional)
    @return List of dictionaries containing query results
    @throws DatabaseError If query execution fails

    Example:
        >>> results = manager.execute_query("SELECT * FROM users WHERE id = ?", (123,))
        >>> print(results[0]['name'])
    """
```

### Type Hints

Always include type hints:

```python
from typing import Any, Dict, List, Optional, Tuple

def process_data(
    data: List[Dict[str, Any]],
    config: Optional[Dict[str, str]] = None
) -> Tuple[bool, str]:
    """Process data and return status."""
    pass
```

## Testing Guidelines

### Test Organization

Tests are organized in the `test/` directory:

```
test/
├── test_config_manager.py      # Configuration tests
├── test_logger_manager.py      # Logging tests
├── test_db2_manager.py          # Database tests
├── test_mq_manager.py           # Messaging tests
├── test_adapters.py             # Adapter tests
├── test_factory.py              # Factory pattern tests
├── test_integration.py          # Integration tests
└── test_cli.py                  # CLI tests
```

### Writing Tests

```python
import unittest
from commonpython.config import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Test suite for ConfigManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager()

    def test_get_config_value(self):
        """Test retrieving configuration value."""
        # Arrange
        self.config_manager.set('test.key', 'value')

        # Act
        result = self.config_manager.get('test.key')

        # Assert
        self.assertEqual(result, 'value')

    def tearDown(self):
        """Clean up after tests."""
        pass
```

### Test Coverage

- Aim for **>80% code coverage**
- Write tests for:
  - Happy path scenarios
  - Error conditions
  - Edge cases
  - Integration points

```bash
# Run tests with coverage
python scripts/test_commonpython.py --coverage

# View detailed coverage report
coverage report -m
```

### Mocking

Use mocks for external dependencies:

```python
from unittest.mock import Mock, patch

@patch('commonpython.database.db2_manager.subprocess.run')
def test_database_query(self, mock_run):
    """Test database query with mocked subprocess."""
    # Setup mock
    mock_run.return_value = Mock(returncode=0, stdout='result')

    # Test your code
    result = manager.execute_query("SELECT * FROM test")

    # Verify
    mock_run.assert_called_once()
```

## Documentation

### Code Documentation

- **All public APIs** must have docstrings
- **Complex logic** should have inline comments
- **Examples** should be included in docstrings

### README Updates

Update the README.md when:
- Adding new features
- Changing installation steps
- Modifying configuration options
- Adding new examples

### Architecture Documentation

Update `docs/` when:
- Changing system architecture
- Adding new design patterns
- Modifying core components

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure all documentation is current
2. **Add Tests**: Include tests for new features or bug fixes
3. **Pass All Checks**: Ensure all tests and linting pass
4. **Update CHANGELOG**: Add entry to CHANGELOG.md
5. **Create PR**: Use the pull request template

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. Automated checks must pass (tests, linting, formatting)
2. At least one maintainer must review
3. Address all review comments
4. Maintainer will merge when approved

## Release Process

### Version Numbers

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml` and `commonpython/__init__.py`
2. Update CHANGELOG.md
3. Create release commit: `git commit -m "chore: release v2.1.0"`
4. Create tag: `git tag -a v2.1.0 -m "Release v2.1.0"`
5. Push: `git push origin main --tags`
6. Create GitHub release with notes

## Getting Help

### Resources

- **Documentation**: [README.md](README.md), [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/psanodiya94/commonpython/issues)
- **Examples**: [examples/](examples/)

### Questions?

- Open a [GitHub Discussion](https://github.com/psanodiya94/commonpython/discussions)
- Or create an issue with the `question` label

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for each release
- GitHub contributors page
- Project README (for significant contributions)

---

Thank you for contributing to CommonPython! Your efforts help make this framework better for everyone.
