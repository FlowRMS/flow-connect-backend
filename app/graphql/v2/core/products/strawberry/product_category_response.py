from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product import ProductCategory

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ProductCategoryResponse(DTOMixin[ProductCategory]):
    id: UUID
    title: str
    factory_id: UUID | None
    commission_rate: Decimal

    @classmethod
    def from_orm_model(cls, model: ProductCategory) -> Self:
        return cls(
            id=model.id,
            title=model.title,
            factory_id=model.factory_id,
            commission_rate=model.commission_rate,
        )
