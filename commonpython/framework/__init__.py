"""
Component Framework for CommonPython

Provides a common framework for running components with shared functionality
including configuration, logging, database, and messaging capabilities.
"""

from .component_runner import ComponentRunner, ComponentBase, run_component, run_component_with_config
from .component_registry import ComponentRegistry, register_component, get_component, list_components

__all__ = ['ComponentRunner', 'ComponentBase', 'ComponentRegistry', 'run_component', 'run_component_with_config', 'register_component', 'get_component', 'list_components']
