import strawberry
from commons.db.v6.core.factories.factory import Factory

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class FactoryInput(BaseInputGQL[Factory]):
    title: str
    published: bool = False

    def to_orm_model(self) -> Factory:
        return Factory(
            title=self.title,
            published=self.published,
        )
