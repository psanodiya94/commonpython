"""
Component Registry for CommonPython Framework

Provides a registry for managing and discovering components.
"""


from .component_base import ComponentBase


class ComponentRegistry:
    """
    Registry for managing components.

    Provides a central registry for discovering and managing components
    that use the CommonPython framework.
    """

    def __init__(self):
        """
        Initialize the component registry.

        @brief Initialize empty component registry.
        """
        self._components: dict[str, type[ComponentBase]] = {}

    def register(self, name: str, component_class: type[ComponentBase]) -> None:
        """
        Register a component.

        @brief Register a component class with the registry.
        @param name Component name
        @param component_class Component class that inherits from ComponentBase
        @throws ValueError If component name already exists
        """
        if name in self._components:
            raise ValueError(f"Component '{name}' is already registered")

        self._components[name] = component_class

    def unregister(self, name: str) -> None:
        """
        Unregister a component.

        @brief Remove a component from the registry.
        @param name Component name
        @throws KeyError If component name not found
        """
        if name not in self._components:
            raise KeyError(f"Component '{name}' not found in registry")

        del self._components[name]

    def get_component(self, name: str) -> type[ComponentBase]:
        """
        Get a registered component.

        @brief Get component class by name.
        @param name Component name
        @return Component class
        @throws KeyError If component name not found
        """
        if name not in self._components:
            raise KeyError(f"Component '{name}' not found in registry")

        return self._components[name]

    def list_components(self) -> list[str]:
        """
        List all registered components.

        @brief Get list of all registered component names.
        @return List of component names
        """
        return list(self._components.keys())

    def is_registered(self, name: str) -> bool:
        """
        Check if component is registered.

        @brief Check if component name exists in registry.
        @param name Component name
        @return True if component is registered, False otherwise
        """
        return name in self._components

    def get_component_count(self) -> int:
        """
        Get number of registered components.

        @brief Get total number of registered components.
        @return Number of registered components
        """
        return len(self._components)

    def clear(self) -> None:
        """
        Clear all registered components.

        @brief Remove all components from registry.
        """
        self._components.clear()


# Global component registry instance
component_registry = ComponentRegistry()


def register_component(name: str, component_class: type[ComponentBase]) -> None:
    """
    Register a component with the global registry.

    @brief Convenience function to register a component.
    @param name Component name
    @param component_class Component class that inherits from ComponentBase
    """
    component_registry.register(name, component_class)


def get_component(name: str) -> type[ComponentBase]:
    """
    Get a component from the global registry.

    @brief Convenience function to get a component.
    @param name Component name
    @return Component class
    """
    return component_registry.get_component(name)


def list_components() -> list[str]:
    """
    List all components in the global registry.

    @brief Convenience function to list all components.
    @return List of component names
    """
    return component_registry.list_components()
