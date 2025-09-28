#!/usr/bin/env python3
"""
Setup script for CommonPython Framework

A common Python framework with config, logging, DB2, MQ, and CLI functionality
using only standard Python modules and IBM CLI interfaces.
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
    description="A common Python framework with config, logging, DB2, MQ, and CLI functionality using standard modules only",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/commonpython",
    packages=find_packages(),
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
    ],
    python_requires=">=3.8",
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
    extras_require={
        "test": ["coverage>=7.0.0"],
    },
)