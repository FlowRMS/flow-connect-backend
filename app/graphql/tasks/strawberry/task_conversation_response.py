"""GraphQL output types for task conversations."""

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.tasks.models.task_conversation_model import TaskConversation


@strawberry.type
class TaskConversationType(DTOMixin[TaskConversation]):
    id: UUID
    created_at: datetime
    created_by: UUID
    task_id: UUID
    content: str

    @classmethod
    def from_orm_model(cls, model: TaskConversation) -> Self:
        return cls(
            id=model.id,
            created_at=model.created_at,
            created_by=model.created_by,
            task_id=model.task_id,
            content=model.content,
        )
