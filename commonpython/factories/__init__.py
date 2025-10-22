"""
Factories for CommonPython Framework

Provides factory classes for creating manager instances based on configuration.
Supports multiple implementation types (CLI, library) with automatic fallback.
"""

from .manager_factory import ManagerFactory

__all__ = ["ManagerFactory"]
