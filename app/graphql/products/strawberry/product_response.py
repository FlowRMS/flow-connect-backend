"""GraphQL response type for PreOpportunity."""

from typing import Self
from uuid import UUID

import strawberry
from commons.db.models.core.product import Product

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ProductResponse(DTOMixin[Product]):
    id: UUID
    factory_id: UUID
    factory_part_number: str

    @classmethod
    def from_orm_model(cls, model: Product) -> Self:
        return cls(
            id=model.id,
            factory_id=model.factory_id,
            factory_part_number=model.factory_part_number,
        )
