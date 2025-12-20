"""GraphQL response type for Factory."""

from typing import Self
from uuid import UUID

import strawberry
from commons.db.models import Factory

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class FactoryResponse(DTOMixin[Factory]):
    id: UUID
    title: str

    @classmethod
    def from_orm_model(cls, model: Factory) -> Self:
        return cls(
            id=model.id,
            title=model.title,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/core/factories/list/{self.id}"
