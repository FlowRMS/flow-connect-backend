from uuid import UUID

import strawberry
from commons.db.v6.crm.tasks.task_conversation_model import TaskConversation

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class TaskConversationInput(BaseInputGQL[TaskConversation]):
    task_id: UUID
    content: str

    def to_orm_model(self) -> TaskConversation:
        return TaskConversation(
            task_id=self.task_id,
            content=self.content,
        )
