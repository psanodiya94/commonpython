#!/usr/bin/env python3
"""
Comprehensive Test Framework for CommonPython

Runs all test cases with detailed reporting, coverage analysis, and categorization.
Supports testing of both CLI and library-based adapter implementations.
"""

import os
import sys
import time
import unittest
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCategories:
    """Test suite categories for organized reporting"""

    CORE = "Core Framework"
    ADAPTERS = "Adapter Pattern"
    INTEGRATION = "Integration Tests"
    CLI = "CLI Interface"
    DATABASE = "Database Operations"
    MESSAGING = "Messaging Operations"
    CONFIG = "Configuration"
    LOGGING = "Logging"
    COMPONENTS = "Components"


class ColoredOutput:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def supports_color():
        """Check if terminal supports colors"""
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Add color to text if supported"""
        if cls.supports_color():
            return f"{color}{text}{cls.ENDC}"
        return text


def categorize_test(test_name: str) -> str:
    """Categorize test based on its name"""
    if "adapter" in test_name.lower():
        return TestCategories.ADAPTERS
    elif "integration" in test_name.lower():
        return TestCategories.INTEGRATION
    elif "cli" in test_name.lower():
        return TestCategories.CLI
    elif "db2" in test_name.lower() or "database" in test_name.lower():
        return TestCategories.DATABASE
    elif "mq" in test_name.lower() or "messaging" in test_name.lower():
        return TestCategories.MESSAGING
    elif "config" in test_name.lower():
        return TestCategories.CONFIG
    elif "logger" in test_name.lower() or "logging" in test_name.lower():
        return TestCategories.LOGGING
    elif "component" in test_name.lower():
        return TestCategories.COMPONENTS
    else:
        return TestCategories.CORE


def check_adapter_availability():
    """Check which adapter implementations are available"""
    try:
        from commonpython.factories import ManagerFactory

        available = ManagerFactory.get_available_implementations()
        return available
    except Exception as e:
        return {
            "database": {"cli": True, "library": False},
            "messaging": {"cli": True, "library": False},
            "error": str(e),
        }


def print_section(title: str, char: str = "=", width: int = 80):
    """Print a formatted section header"""
    print()
    print(ColoredOutput.colorize(char * width, ColoredOutput.HEADER))
    print(ColoredOutput.colorize(title.center(width), ColoredOutput.BOLD))
    print(ColoredOutput.colorize(char * width, ColoredOutput.HEADER))


def print_subsection(title: str, char: str = "-", width: int = 80):
    """Print a formatted subsection header"""
    print()
    print(ColoredOutput.colorize(f"{title}", ColoredOutput.OKBLUE))
    print(ColoredOutput.colorize(char * width, ColoredOutput.OKBLUE))


def discover_tests(test_dir: Path) -> List[str]:
    """Discover all test files"""
    test_files = []
    for test_file in sorted(test_dir.glob("test_*.py")):
        test_files.append(test_file.stem)
    return test_files


class DetailedTestResult(unittest.TextTestResult):
    """Enhanced test result with categorization"""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_times: Dict[str, float] = {}
        self.category_stats: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0}
        )
        self.start_time: Optional[float] = None

    def startTest(self, test):
        super().startTest(test)
        self.start_time = time.time()

    def stopTest(self, test):
        super().stopTest(test)
        if self.start_time:
            duration = time.time() - self.start_time
            self.test_times[str(test)] = duration

            # Categorize test
            category = categorize_test(str(test))
            self.category_stats[category]["total"] += 1

    def addSuccess(self, test):
        super().addSuccess(test)
        category = categorize_test(str(test))
        self.category_stats[category]["passed"] += 1

    def addFailure(self, test, err):
        super().addFailure(test, err)
        category = categorize_test(str(test))
        self.category_stats[category]["failed"] += 1

    def addError(self, test, err):
        super().addError(test, err)
        category = categorize_test(str(test))
        self.category_stats[category]["errors"] += 1

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        category = categorize_test(str(test))
        self.category_stats[category]["skipped"] += 1


class DetailedTestRunner(unittest.TextTestRunner):
    """Enhanced test runner with detailed reporting"""

    resultclass = DetailedTestResult


def run_comprehensive_tests(suite_filter: Optional[str] = None, verbosity: int = 2):
    """
    Run comprehensive test suite with detailed reporting.

    @brief Execute all test cases with comprehensive reporting.
    @param suite_filter Optional filter for specific test suites
    @param verbosity Verbosity level for test output
    @return Test result object
    """
    print_section("CommonPython Framework - Comprehensive Test Suite")

    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Test Filter: {suite_filter or 'All Tests'}")

    # Check adapter availability
    print()
    print(ColoredOutput.colorize("Adapter Implementation Availability:", ColoredOutput.OKBLUE))
    available = check_adapter_availability()

    if "error" not in available:
        db_cli = "✓" if available["database"]["cli"] else "✗"
        db_lib = "✓" if available["database"]["library"] else "✗"
        mq_cli = "✓" if available["messaging"]["cli"] else "✗"
        mq_lib = "✓" if available["messaging"]["library"] else "✗"

        print(f"  Database: CLI {db_cli}  Library (ibm_db) {db_lib}")
        print(f"  Messaging: CLI {mq_cli}  Library (pymqi) {mq_lib}")
    else:
        print(f"  Warning: Could not check adapter availability: {available.get('error')}")

    # Discover tests
    test_dir = Path(__file__).parent.parent / "test"
    test_files = discover_tests(test_dir)

    print()
    print(ColoredOutput.colorize("Discovered Test Suites:", ColoredOutput.OKBLUE))
    for test_file in test_files:
        print(f"  • {test_file}")

    # Discover and run tests
    print_subsection("Running Tests")

    loader = unittest.TestLoader()

    if suite_filter:
        # Run specific test suite
        pattern = f"test_{suite_filter}*.py"
        suite = loader.discover(test_dir, pattern=pattern)
    else:
        # Run all tests
        suite = loader.discover(test_dir, pattern="test_*.py")

    # Create detailed test runner
    runner = DetailedTestRunner(
        verbosity=verbosity, stream=sys.stdout, descriptions=True, failfast=False
    )

    # Run tests with timing
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()

    # Print detailed summary
    print_section("TEST EXECUTION SUMMARY")

    # Overall statistics
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, "skipped") else 0
    passed = total_tests - failures - errors - skipped
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    print(f"Total Tests: {ColoredOutput.colorize(str(total_tests), ColoredOutput.BOLD)}")
    print(f"Passed: {ColoredOutput.colorize(str(passed), ColoredOutput.OKGREEN)}")
    print(
        f"Failed: {ColoredOutput.colorize(str(failures), ColoredOutput.FAIL if failures > 0 else ColoredOutput.OKGREEN)}"
    )
    print(
        f"Errors: {ColoredOutput.colorize(str(errors), ColoredOutput.FAIL if errors > 0 else ColoredOutput.OKGREEN)}"
    )
    print(
        f"Skipped: {ColoredOutput.colorize(str(skipped), ColoredOutput.WARNING if skipped > 0 else ColoredOutput.OKGREEN)}"
    )
    print(
        f"Success Rate: {ColoredOutput.colorize(f'{success_rate:.1f}%', ColoredOutput.OKGREEN if success_rate == 100 else ColoredOutput.WARNING)}"
    )
    print(
        f"Execution Time: {ColoredOutput.colorize(f'{end_time - start_time:.2f}s', ColoredOutput.OKCYAN)}"
    )

    # Category breakdown
    if hasattr(result, "category_stats") and result.category_stats:
        print_subsection("Tests by Category")

        for category in sorted(result.category_stats.keys()):
            stats = result.category_stats[category]
            total = stats["total"]
            passed = stats["passed"]
            failed = stats["failed"]
            errors = stats["errors"]
            skipped = stats["skipped"]

            print(f"\n{ColoredOutput.colorize(category, ColoredOutput.BOLD)}")
            print(
                f"  Total: {total} | Passed: {passed} | Failed: {failed} | Errors: {errors} | Skipped: {skipped}"
            )

    # Performance metrics
    if hasattr(result, "test_times") and result.test_times:
        print_subsection("Performance Metrics")

        avg_time = sum(result.test_times.values()) / len(result.test_times)
        slowest_tests = sorted(result.test_times.items(), key=lambda x: x[1], reverse=True)[:5]

        print(f"Average Test Time: {avg_time:.3f}s")
        print("\nSlowest Tests:")
        for test_name, duration in slowest_tests:
            print(f"  {duration:.3f}s - {test_name}")

    # Print failure details
    if result.failures:
        print_section("FAILURE DETAILS", "=")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n{ColoredOutput.colorize(f'{i}. {test}', ColoredOutput.FAIL)}")
            print("-" * 80)
            print(traceback)

    # Print error details
    if result.errors:
        print_section("ERROR DETAILS", "=")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n{ColoredOutput.colorize(f'{i}. {test}', ColoredOutput.FAIL)}")
            print("-" * 80)
            print(traceback)

    # Print skipped test details
    if hasattr(result, "skipped") and result.skipped:
        print_section("SKIPPED TESTS", "=")
        for i, (test, reason) in enumerate(result.skipped, 1):
            print(f"{i}. {test}: {ColoredOutput.colorize(reason, ColoredOutput.WARNING)}")

    return result


def run_tests_with_coverage(suite_filter: Optional[str] = None, verbosity: int = 2):
    """
    Run tests with coverage analysis.

    @brief Execute tests with coverage reporting if available.
    @param suite_filter Optional filter for specific test suites
    @param verbosity Verbosity level for test output
    @return Test result object
    """
    try:
        import coverage

        print(
            ColoredOutput.colorize("Running tests with coverage analysis...", ColoredOutput.OKBLUE)
        )

        # Start coverage
        cov = coverage.Coverage(
            source=["commonpython"],
            omit=["test/*", "*/test_*.py", "*/__init__.py", "*/cli.py"],  # CLI has its own tests
        )
        cov.start()

        # Run tests
        result = run_comprehensive_tests(suite_filter, verbosity)

        # Stop coverage
        cov.stop()
        cov.save()

        # Generate coverage report
        print_section("COVERAGE REPORT")

        cov.report(show_missing=True)

        # Coverage by module
        print_subsection("Coverage by Module")

        # Get coverage data
        data = cov.get_data()
        files = data.measured_files()

        module_coverage = {}
        for filename in sorted(files):
            if "commonpython" in filename:
                analysis = cov.analysis(filename)
                executed = len(analysis[1])
                missing = len(analysis[2])
                total = executed + missing
                if total > 0:
                    coverage_pct = (executed / total) * 100
                    module_name = Path(filename).stem
                    module_coverage[module_name] = coverage_pct

        for module, pct in sorted(module_coverage.items()):
            color = (
                ColoredOutput.OKGREEN
                if pct >= 80
                else ColoredOutput.WARNING if pct >= 60 else ColoredOutput.FAIL
            )
            print(f"  {module:30s} {ColoredOutput.colorize(f'{pct:5.1f}%', color)}")

        # Generate HTML coverage report
        try:
            html_dir = Path(__file__).parent.parent / "htmlcov"
            cov.html_report(directory=str(html_dir), title="CommonPython Framework Coverage")
            print(
                f"\n{ColoredOutput.colorize('✓', ColoredOutput.OKGREEN)} HTML coverage report: {html_dir}/index.html"
            )
        except Exception as e:
            print(
                f"{ColoredOutput.colorize('✗', ColoredOutput.FAIL)} Could not generate HTML report: {e}"
            )

        return result

    except ImportError:
        print(
            ColoredOutput.colorize(
                "Warning: Coverage module not available. Running tests without coverage.",
                ColoredOutput.WARNING,
            )
        )
        print("Install with: pip install coverage")
        return run_comprehensive_tests(suite_filter, verbosity)


def main():
    """
    Main test runner function.

    @brief Main entry point for comprehensive test framework.
    """
    # Parse command line arguments
    args = sys.argv[1:]

    run_coverage = "--coverage" in args or "--cov" in args
    verbose = "--verbose" in args or "-v" in args
    quiet = "--quiet" in args or "-q" in args
    list_tests = "--list" in args

    # Extract suite filter if provided
    suite_filter = None
    for arg in args:
        if not arg.startswith("--") and not arg.startswith("-"):
            suite_filter = arg
            break

    # Set verbosity
    verbosity = 2
    if verbose:
        verbosity = 3
    elif quiet:
        verbosity = 1

    # List tests and exit
    if list_tests:
        test_dir = Path(__file__).parent.parent / "test"
        test_files = discover_tests(test_dir)
        print("Available Test Suites:")
        for test_file in test_files:
            print(f"  • {test_file}")
        print(f"\nTotal: {len(test_files)} test suites")
        print("\nRun specific suite: python test_commonpython.py <suite_name>")
        print("Example: python test_commonpython.py adapters")
        return

    # Print header
    print()
    print(ColoredOutput.colorize("╔" + "═" * 78 + "╗", ColoredOutput.HEADER))
    print(
        ColoredOutput.colorize(
            "║" + "CommonPython Framework - Test Runner".center(78) + "║", ColoredOutput.HEADER
        )
    )
    print(ColoredOutput.colorize("╚" + "═" * 78 + "╝", ColoredOutput.HEADER))

    # Run tests
    try:
        if run_coverage:
            result = run_tests_with_coverage(suite_filter, verbosity)
        else:
            result = run_comprehensive_tests(suite_filter, verbosity)

        # Print final status
        print()
        print("=" * 80)

        if result.failures or result.errors:
            msg = f"❌ Tests completed with {len(result.failures)} failures and {len(result.errors)} errors"
            print(ColoredOutput.colorize(msg, ColoredOutput.FAIL))
            sys.exit(1)
        else:
            msg = f"✅ All {result.testsRun} tests passed successfully!"
            print(ColoredOutput.colorize(msg, ColoredOutput.OKGREEN))
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n" + ColoredOutput.colorize("Tests interrupted by user", ColoredOutput.WARNING))
        sys.exit(130)
    except Exception as e:
        print("\n\n" + ColoredOutput.colorize(f"Error running tests: {e}", ColoredOutput.FAIL))
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
