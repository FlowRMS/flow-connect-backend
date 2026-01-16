from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.tasks import TaskCategory

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class TaskCategoryType(DTOMixin[TaskCategory]):
    id: UUID
    name: str
    display_order: int
    is_active: bool
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: TaskCategory) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            display_order=model.display_order,
            is_active=model.is_active,
            created_at=model.created_at,
        )
