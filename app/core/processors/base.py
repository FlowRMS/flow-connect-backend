from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from commons.db.v6 import BaseModel

from app.core.processors.context import EntityContext
from app.core.processors.events import RepositoryEvent

T = TypeVar("T", bound=BaseModel)


class BaseProcessor(ABC, Generic[T]):
    """Abstract base class for entity lifecycle processors."""

    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def events(self) -> list[RepositoryEvent]:
        """Events this processor handles."""
        ...

    @abstractmethod
    async def process(self, context: EntityContext[T]) -> None:
        """Execute processor logic."""
        ...
