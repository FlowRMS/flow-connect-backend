import importlib
import inspect
import pkgutil
from collections.abc import Iterable
from types import ModuleType as Module
from typing import Any

import aioinject


def discover_classes(
    module: Module,
    module_suffix: str,
    class_suffix: str,
) -> list[Any]:
    """
    Discover classes in a module by module and class suffix patterns.

    Args:
        module: The root module to search in
        module_suffix: Only scan modules ending with this suffix
        class_suffix: Only return classes ending with this suffix
    """
    mods = pkgutil.walk_packages(
        module.__path__,
        prefix=module.__name__ + ".",
    )
    matching_modules = [mod for mod in mods if mod.name.endswith(module_suffix)]
    classes: list[Any] = []

    for mod in matching_modules:
        try:
            imported_module = importlib.import_module(mod.name)
        except Exception as e:
            raise ImportError(f"Failed to import module {mod.name}: {e}") from e

        for _, obj in inspect.getmembers(imported_module, inspect.isclass):
            if obj.__module__ == mod.name and obj.__name__.endswith(class_suffix):
                classes.append(obj)

    return classes


def discover_types(
    module: Module,
    class_suffix: str,
) -> list[Any]:
    """
    Discover Strawberry types in modules containing 'strawberry' in their name.

    Args:
        module: The root module to search in
        class_suffix: Only return classes ending with this suffix
    """
    mods = pkgutil.walk_packages(
        module.__path__,
        prefix=module.__name__ + ".",
    )
    strawberry_modules = [mod for mod in mods if "strawberry" in mod.name]
    classes: list[Any] = []

    for mod in strawberry_modules:
        try:
            imported_module = importlib.import_module(mod.name)
        except Exception as e:
            raise ImportError(f"Failed to import module {mod.name}: {e}") from e

        for _, obj in inspect.getmembers(imported_module, inspect.isclass):
            if obj.__name__.endswith(class_suffix):
                classes.append(obj)

    return classes


def discover_providers(
    modules: list[Module] | Module,
    class_suffix: str,
) -> Iterable[aioinject.Provider[Any]]:
    """
    Discover classes and wrap them as aioinject Scoped providers.

    Args:
        modules: Module or list of modules to search in
        class_suffix: Module suffix and class suffix pattern (e.g., "repository")
    """
    if isinstance(modules, Module):
        modules = [modules]

    providers: list[aioinject.Provider[Any]] = []

    for module in modules:
        classes = discover_classes(
            module,
            module_suffix=class_suffix,
            class_suffix=class_suffix.capitalize(),
        )
        providers.extend(aioinject.Scoped(cls) for cls in classes)

    return providers
