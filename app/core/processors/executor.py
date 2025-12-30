from typing import TypeVar

from commons.db.v6 import BaseModel

from app.core.processors.base import BaseProcessor
from app.core.processors.context import EntityContext

T = TypeVar("T", bound=BaseModel)


class ProcessorExecutor:
    """Executes processors for repository lifecycle events."""

    def __init__(self) -> None:
        super().__init__()

    async def execute(
        self,
        entity_context: EntityContext[T],
        processor_classes: list[BaseProcessor],
    ) -> None:
        for processor_class in processor_classes:
            await processor_class.process(entity_context)
