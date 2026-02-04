import importlib
import inspect
import pkgutil
from collections.abc import Iterable
from types import ModuleType as Module
from typing import Any

import aioinject


def discover_providers(
    modules: list[Module] | Module,
    class_suffix: str = "repository",
) -> Iterable[aioinject.Provider[Any]]:
    providers: Iterable[aioinject.Provider[Any]] = []
    repository_classes: Iterable[pkgutil.ModuleInfo] = []
    if isinstance(modules, Module):
        modules = [modules]
    for module in modules:
        mods = pkgutil.walk_packages(
            module.__path__,
            prefix=module.__name__ + ".",
        )
        repository_classes.extend(
            [
                mod
                for mod in mods
                if mod.name.endswith(class_suffix) and ".tests." not in mod.name
            ]
        )

    for mod in repository_classes:
        try:
            module = importlib.import_module(mod.name)
        except Exception as e:
            raise ImportError(f"Failed to import module {mod.name}: {e}") from e

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == mod.name and obj.__name__.endswith(
                class_suffix.capitalize()
            ):
                providers.append(aioinject.Scoped(obj))

    return providers
