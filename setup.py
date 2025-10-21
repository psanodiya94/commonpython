#!/usr/bin/env python3
"""
Setup script for CommonPython Framework

A common Python framework with config, logging, DB2, MQ, and CLI functionality.
Supports both CLI-based and library-based implementations via adapter pattern.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    """
    Read the README file.
    
    @brief Read and return the contents of the README file.
    @return README file contents
    """
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    """
    Read requirements from requirements.txt.
    
    @brief Read and return requirements from requirements file.
    @return List of requirements
    """
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="commonpython",
    version="2.0.0",
    author="CommonPython Framework Team",
    author_email="team@commonpython.com",
    description="A flexible Python framework with adapter pattern for IBM DB2 and MQ integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/commonpython",
    packages=find_packages(exclude=["test", "test.*", "scripts"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.8",
    # Mandatory dependencies (always required)
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "commonpython=commonpython.cli.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "commonpython": ["config/*.yaml", "config/*.json"],
    },
    test_suite="test.run_tests",
    # Optional dependencies (install as needed)
    extras_require={
        # Development and testing
        "dev": [
            "coverage>=7.0.0",
        ],
        "test": [
            "coverage>=7.0.0",
        ],
        # Library-based implementations (high performance)
        "library": [
            "ibm_db>=3.0.0",
            "pymqi>=1.12.0",
        ],
        # Database library support only
        "db-library": [
            "ibm_db>=3.0.0",
        ],
        # Messaging library support only
        "mq-library": [
            "pymqi>=1.12.0",
        ],
        # All optional dependencies
        "all": [
            "coverage>=7.0.0",
            "ibm_db>=3.0.0",
            "pymqi>=1.12.0",
        ],
    },
)