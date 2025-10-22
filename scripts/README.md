# CommonPython Test Scripts

This directory contains test and utility scripts for the CommonPython framework.

## test_commonpython.py

Enhanced comprehensive test runner with categorization, performance metrics, and coverage analysis.

### Features

- ✅ **Category-based Reporting**: Tests grouped by functionality (Adapters, CLI, Database, etc.)
- ✅ **Performance Metrics**: Identifies slowest tests and average execution time
- ✅ **Adapter Availability Check**: Shows which implementations (CLI/Library) are available
- ✅ **Colored Output**: Beautiful terminal output with color coding
- ✅ **Coverage Analysis**: Generate HTML coverage reports
- ✅ **Selective Test Execution**: Run specific test suites
- ✅ **Detailed Summaries**: Category breakdown, failure details, skipped tests

### Usage

#### Run All Tests

```bash
python scripts/test_commonpython.py
```

#### Run with Coverage

```bash
python scripts/test_commonpython.py --coverage
```

This generates:

- Console coverage report
- HTML coverage report in `htmlcov/` directory

#### Run Specific Test Suite

```bash
# Run only adapter tests
python scripts/test_commonpython.py adapters

# Run only integration tests
python scripts/test_commonpython.py integration

# Run only CLI tests
python scripts/test_commonpython.py cli
```

#### List Available Test Suites

```bash
python scripts/test_commonpython.py --list
```

#### Verbosity Options

```bash
# Verbose mode (more details)
python scripts/test_commonpython.py -v

# Quiet mode (less output)
python scripts/test_commonpython.py -q
```

### Command Line Options

| Option                | Description                                           |
| --------------------- | ----------------------------------------------------- |
| `--coverage`, `--cov` | Run tests with coverage analysis                      |
| `--verbose`, `-v`     | Increase output verbosity                             |
| `--quiet`, `-q`       | Decrease output verbosity                             |
| `--list`              | List all available test suites                        |
| `<suite_name>`        | Run specific test suite (e.g., `adapters`, `factory`) |

### Examples

```bash
# Run all tests with coverage in verbose mode
python scripts/test_commonpython.py --coverage -v

# Run only factory tests quietly
python scripts/test_commonpython.py factory -q

# List all available test suites
python scripts/test_commonpython.py --list

# Run integration tests with coverage
python scripts/test_commonpython.py integration --cov
```

### Output Categories

Tests are automatically categorized:

- **Adapter Pattern**: Tests for CLI and library adapters
- **Integration Tests**: Cross-component integration tests
- **CLI Interface**: Command-line interface tests
- **Database Operations**: DB2 manager tests
- **Messaging Operations**: MQ manager tests
- **Configuration**: Config manager tests
- **Logging**: Logger manager tests
- **Components**: Component framework tests
- **Core Framework**: Factory and other core tests

### Exit Codes

- `0`: All tests passed
- `1`: Tests failed or had errors
- `130`: Tests interrupted by user (Ctrl+C)

### Sample Output

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                     CommonPython Framework - Test Runner                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
               CommonPython Framework - Comprehensive Test Suite
================================================================================

Adapter Implementation Availability:
  Database: CLI ✓  Library (ibm_db) ✗
  Messaging: CLI ✓  Library (pymqi) ✗

Discovered Test Suites:
  • test_adapters
  • test_cli
  • test_component
  ...

================================================================================
                             TEST EXECUTION SUMMARY
================================================================================
Total Tests: 295
Passed: 295
Failed: 0
Errors: 0
Skipped: 0
Success Rate: 100.0%
Execution Time: 0.42s

Tests by Category
--------------------------------------------------------------------------------

Adapter Pattern
  Total: 19 | Passed: 19 | Failed: 0 | Errors: 0 | Skipped: 0

Database Operations
  Total: 44 | Passed: 44 | Failed: 0 | Errors: 0 | Skipped: 0

...

Performance Metrics
--------------------------------------------------------------------------------
Average Test Time: 0.001s

Slowest Tests:
  0.008s - test_main_database_execute
  0.006s - test_setup_database_failure
  ...

✅ All 295 tests passed successfully!
```

## Tips

1. **Use Coverage Regularly**: Run with `--coverage` to identify untested code
1. **Test Specific Suites**: Speed up development by testing only what you changed
1. **Check Adapter Availability**: The runner shows which implementations are available
1. **View HTML Coverage**: Open `htmlcov/index.html` in your browser for detailed coverage
1. **Monitor Performance**: Check slowest tests to identify optimization opportunities

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests with coverage and fail on any error
python scripts/test_commonpython.py --coverage || exit 1
```

## Troubleshooting

### Colors Not Showing

The script automatically detects terminal color support. If colors aren't showing:

- Ensure your terminal supports ANSI colors
- Try a different terminal emulator

### Coverage Module Not Found

Install coverage:

```bash
pip install coverage
```

### Tests Not Discovered

Ensure:

- Test files are in `test/` directory
- Test files follow naming pattern `test_*.py`
- Test classes inherit from `unittest.TestCase`
