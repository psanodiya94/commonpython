"""
Configuration Management Module

Provides centralized configuration management with support for YAML configuration
files, environment variables, and default configurations using only standard
Python modules.

@brief Configuration management functionality for CommonPython Framework
@author CommonPython Framework Team
@version 2.0.0
@since 1.0.0
"""

from .config_manager import ConfigManager

__all__ = ['ConfigManager']