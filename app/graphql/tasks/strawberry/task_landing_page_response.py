from datetime import date
from typing import Any, Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.tasks.task_priority import TaskPriority
from commons.db.v6.crm.tasks.task_status import TaskStatus
from sqlalchemy.engine.row import Row

from app.core.db.adapters.dto import LandingPageInterfaceBase
from app.graphql.common.linked_entity import LinkedEntity


@strawberry.type(name="TaskLandingPage")
class TaskLandingPageResponse(LandingPageInterfaceBase):
    title: str
    status: TaskStatus
    priority: TaskPriority
    description: str | None
    assigned_to: str | None  # Deprecated: use assignees field
    assignees: list[str]
    due_date: date | None
    reminder_date: date | None
    tags: list[str] | None
    linked_entities: list[LinkedEntity]

    @classmethod
    def from_orm_model(cls, row: Row[Any]) -> Self:
        data = cls.unpack_row(row)
        linked_entities_data = data.pop("linked_entities", [])
        data["linked_entities"] = [
            LinkedEntity(
                id=UUID(item["id"]),
                title=item["title"],
                entity_type=EntityType(item["entity_type"]),
            )
            for item in linked_entities_data
        ]
        # Parse assignees from JSON array
        assignees_data = data.pop("assignees", []) or []
        data["assignees"] = [
            item["name"] for item in assignees_data if item.get("name")
        ]
        return cls(**data)
