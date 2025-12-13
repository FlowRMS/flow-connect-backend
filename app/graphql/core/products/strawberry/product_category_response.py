from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.core.products.models import ProductCategoryV2


@strawberry.type
class ProductCategoryResponse(DTOMixin[ProductCategoryV2]):
    id: UUID
    title: str
    factory_id: UUID
    commission_rate: Decimal

    @classmethod
    def from_orm_model(cls, model: ProductCategoryV2) -> Self:
        return cls(
            id=model.id,
            title=model.title,
            factory_id=model.factory_id,
            commission_rate=model.commission_rate,
        )
