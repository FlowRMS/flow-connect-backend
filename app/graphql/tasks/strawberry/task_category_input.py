import strawberry
from commons.db.v6.crm.tasks import TaskCategory

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CreateTaskCategoryInput(BaseInputGQL[TaskCategory]):
    name: str
    display_order: int = 0

    def to_orm_model(self) -> TaskCategory:
        return TaskCategory(
            name=self.name,
            display_order=self.display_order,
            is_active=True,
        )


@strawberry.input
class UpdateTaskCategoryInput(BaseInputGQL[TaskCategory]):
    name: str | None = strawberry.UNSET
    display_order: int | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET

    def to_orm_model(self) -> TaskCategory:
        return TaskCategory(
            name=self.optional_field(self.name) or "",
            display_order=self.optional_field(self.display_order) or 0,
            is_active=self.optional_field(self.is_active) if self.is_active is not strawberry.UNSET else True,
        )
