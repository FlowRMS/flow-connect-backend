from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.tasks.task_conversation_model import TaskConversation

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class TaskConversationType(DTOMixin[TaskConversation]):
    _instance: strawberry.Private[TaskConversation]
    id: UUID
    created_at: datetime
    task_id: UUID
    content: str

    @classmethod
    def from_orm_model(cls, model: TaskConversation) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            task_id=model.task_id,
            content=model.content,
        )

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)
