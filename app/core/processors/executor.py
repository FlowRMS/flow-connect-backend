from typing import Any, TypeVar

from app.core.db.base import BaseModel
from app.core.processors.context import EntityContext
from app.core.processors.events import RepositoryEvent
from app.core.processors.registry import processor_registry

T = TypeVar("T", bound=BaseModel)


class ProcessorExecutor:
    """Executes processors for repository lifecycle events."""

    def __init__(self) -> None:
        super().__init__()

    async def execute(
        self,
        entity_type: type[T],
        event: RepositoryEvent,
        entity_context: EntityContext[T],
    ) -> None:
        from app.core.container import create_container

        """Execute all processors for an entity/event combination sequentially."""
        processor_classes = processor_registry.get_processors(entity_type, event)

        async with create_container().context() as conn_ctx:
            for processor_class in processor_classes:
                processor: Any = await conn_ctx.resolve(processor_class)
                await processor.process(entity_context)
