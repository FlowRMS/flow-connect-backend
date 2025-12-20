from dataclasses import dataclass
from typing import Generic, TypeVar
from uuid import UUID

from app.core.db.base import BaseModel
from app.core.processors.events import RepositoryEvent

T = TypeVar("T", bound=BaseModel)


@dataclass(frozen=True)
class EntityContext(Generic[T]):
    """Context passed to processors during lifecycle events."""

    entity: T
    entity_id: UUID
    event: RepositoryEvent
    original_entity: T | None = None
