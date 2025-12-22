from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product import ProductUom

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ProductUomResponse(DTOMixin[ProductUom]):
    id: UUID
    title: str
    description: str | None
    multiply: bool
    multiply_by: int

    @classmethod
    def from_orm_model(cls, model: ProductUom) -> Self:
        return cls(
            id=model.id,
            title=model.title,
            description=model.description,
            multiply=model.multiply,
            multiply_by=model.multiply_by,
        )
