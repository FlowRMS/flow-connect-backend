"""GraphQL input types for task conversations."""

from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.tasks.models.task_conversation_model import TaskConversation


@strawberry.input
class TaskConversationInput(BaseInputGQL[TaskConversation]):
    task_id: UUID
    content: str

    def to_orm_model(self) -> TaskConversation:
        return TaskConversation(
            task_id=self.task_id,
            content=self.content,
        )
