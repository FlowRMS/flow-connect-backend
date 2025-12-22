from collections.abc import Callable
from typing import Any, TypeVar

from commons.db.v6 import BaseModel

from app.core.processors.registry import processor_registry

T = TypeVar("T", bound=BaseModel)
P = TypeVar("P")


def entity_processor(entity_type: type[T]) -> Callable[[type[P]], type[P]]:
    """Decorator to register a processor for an entity type."""

    def decorator(processor_class: type[Any]) -> type[Any]:
        processor_registry.register(entity_type, processor_class)
        return processor_class

    return decorator
