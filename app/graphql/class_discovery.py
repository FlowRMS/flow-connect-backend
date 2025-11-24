import importlib
import inspect
import pkgutil
from collections.abc import Iterable
from types import ModuleType as Module
from typing import Any


def class_discovery(
    module: Module,
    mode_suffix: str,
    class_suffix: str,
) -> Iterable[Any]:
    mods = pkgutil.walk_packages(
        module.__path__,
        prefix=module.__name__ + ".",
    )
    mod_classes = [mod for mod in mods if mod.name.endswith(mode_suffix)]
    classes: Iterable[Any] = []

    for mod in mod_classes:
        try:
            module = importlib.import_module(mod.name)
        except Exception as e:
            raise ImportError(f"Failed to import module {mod.name}: {e}") from e

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == mod.name and obj.__name__.endswith(class_suffix):
                classes.append(obj)

    return classes


def types_discovery(
    module: Module,
    class_suffix: str,
) -> Iterable[Any]:
    mods = pkgutil.walk_packages(
        module.__path__,
        prefix=module.__name__ + ".",
    )
    mod_classes = [mod for mod in mods if "strawberry" in mod.name]
    classes: Iterable[Any] = []

    for mod in mod_classes:
        try:
            module = importlib.import_module(mod.name)
        except Exception as e:
            raise ImportError(f"Failed to import module {mod.name}: {e}") from e

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__name__.endswith(class_suffix):
                classes.append(obj)

    return classes
