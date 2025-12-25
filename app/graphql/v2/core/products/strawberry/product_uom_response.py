from decimal import Decimal
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
    division_factor: Decimal | None

    @classmethod
    def from_orm_model(cls, model: ProductUom) -> Self:
        return cls(
            id=model.id,
            title=model.title,
            description=model.description,
            division_factor=model.division_factor,
        )
