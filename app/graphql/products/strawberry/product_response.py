"""GraphQL response type for PreOpportunity."""

import decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.models import Product

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ProductResponse(DTOMixin[Product]):
    id: UUID
    factory_id: UUID
    factory_part_number: str
    unit_price: decimal.Decimal
    default_commission_rate: decimal.Decimal
    description: str | None
    published: bool

    @classmethod
    def from_orm_model(cls, model: Product) -> Self:
        return cls(
            id=model.id,
            factory_id=model.factory_id,
            factory_part_number=model.factory_part_number,
            unit_price=model.unit_price,
            default_commission_rate=model.default_commission_rate,
            description=model.description,
            published=model.published,
        )
