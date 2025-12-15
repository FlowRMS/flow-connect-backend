from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.products.models import ProductUomV2


@strawberry.type
class ProductUomResponse(DTOMixin[ProductUomV2]):
    id: UUID
    title: str
    description: str | None
    multiply: bool
    multiply_by: int

    @classmethod
    def from_orm_model(cls, model: ProductUomV2) -> Self:
        return cls(
            id=model.id,
            title=model.title,
            description=model.description,
            multiply=model.multiply,
            multiply_by=model.multiply_by,
        )
