#!/usr/bin/env python3
"""
Comprehensive Test Framework for CommonPython

Runs all test cases with detailed reporting and coverage analysis.
"""

import unittest
import sys
import os
import time
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def run_comprehensive_tests():
    """
    Run comprehensive test suite with detailed reporting.
    
    @brief Execute all test cases with comprehensive reporting.
    @return Test result object
    """
    print("CommonPython Framework - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent.parent / "test"
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Create detailed test runner
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    # Run tests with timing
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print detailed summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Execution Time: {end_time - start_time:.2f} seconds")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Print failure details
    if result.failures:
        print("\n" + "=" * 60)
        print("FAILURE DETAILS")
        print("=" * 60)
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n{i}. {test}")
            print("-" * 40)
            print(traceback)
    
    # Print error details
    if result.errors:
        print("\n" + "=" * 60)
        print("ERROR DETAILS")
        print("=" * 60)
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n{i}. {test}")
            print("-" * 40)
            print(traceback)
    
    # Print skipped test details
    if hasattr(result, 'skipped') and result.skipped:
        print("\n" + "=" * 60)
        print("SKIPPED TESTS")
        print("=" * 60)
        for i, (test, reason) in enumerate(result.skipped, 1):
            print(f"{i}. {test}: {reason}")
    
    return result

def run_tests_with_coverage():
    """
    Run tests with coverage analysis.
    
    @brief Execute tests with coverage reporting if available.
    @return Test result object
    """
    try:
        import coverage
        
        print("Running tests with coverage analysis...")
        
        # Start coverage
        cov = coverage.Coverage(
            source=['commonpython'],
            omit=['test/*', '*/test_*.py']
        )
        cov.start()
        
        # Run tests
        result = run_comprehensive_tests()
        
        # Stop coverage
        cov.stop()
        cov.save()
        
        # Generate coverage report
        print("\n" + "=" * 60)
        print("COVERAGE REPORT")
        print("=" * 60)
        cov.report(show_missing=True)
        
        # Generate HTML coverage report
        try:
            cov.html_report(directory='htmlcov', title='CommonPython Framework Coverage')
            print(f"\nHTML coverage report generated in htmlcov/ directory")
        except Exception as e:
            print(f"Could not generate HTML report: {e}")
        
        return result
        
    except ImportError:
        print("Coverage module not available. Running tests without coverage.")
        return run_comprehensive_tests()

def main():
    """
    Main test runner function.
    
    @brief Main entry point for comprehensive test framework.
    """
    # Parse command line arguments
    run_coverage = '--coverage' in sys.argv or '--cov' in sys.argv
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    if verbose:
        print("Verbose mode enabled")
    
    # Run tests
    if run_coverage:
        result = run_tests_with_coverage()
    else:
        result = run_comprehensive_tests()
    
    # Exit with appropriate code
    if result.failures or result.errors:
        print(f"\n❌ Tests completed with {len(result.failures)} failures and {len(result.errors)} errors")
        sys.exit(1)
    else:
        print(f"\n✅ All {result.testsRun} tests passed successfully!")
        sys.exit(0)

if __name__ == '__main__':
    main()
