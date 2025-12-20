from collections import defaultdict
from typing import Any

from app.core.db.base import BaseModel
from app.core.processors.events import RepositoryEvent


class ProcessorRegistry:
    """Registry for entity processors. Maintains registration order."""

    def __init__(self) -> None:
        super().__init__()
        self._processors: dict[
            type[BaseModel],
            dict[RepositoryEvent, list[type[Any]]],
        ] = defaultdict(lambda: defaultdict(list))

    def register(
        self,
        entity_type: type[BaseModel],
        processor_class: type[Any],
    ) -> None:
        """Register a processor class for an entity type."""
        instance = object.__new__(processor_class)
        for event in instance.events:
            self._processors[entity_type][event].append(processor_class)

    def get_processors(
        self,
        entity_type: type[BaseModel],
        event: RepositoryEvent,
    ) -> list[type[Any]]:
        """Get processor classes for an entity/event combination."""
        return self._processors[entity_type].get(event, [])


processor_registry = ProcessorRegistry()
