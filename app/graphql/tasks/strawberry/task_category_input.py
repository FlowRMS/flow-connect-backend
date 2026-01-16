from uuid import UUID

import strawberry
from commons.db.v6.crm.tasks import TaskCategory

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class TaskCategoryInput(BaseInputGQL[TaskCategory]):
    id: UUID | None = None
    name: str
    display_order: int = 0

    def to_orm_model(self) -> TaskCategory:
        return TaskCategory(
            name=self.name,
            display_order=self.display_order,
            is_active=True,
        )
