from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product_quantity_pricing import ProductQuantityPricing

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ProductQuantityPricingResponse(DTOMixin[ProductQuantityPricing]):
    _instance: strawberry.Private[ProductQuantityPricing]
    id: UUID
    product_id: UUID
    quantity_low: Decimal
    quantity_high: Decimal
    unit_price: Decimal

    @classmethod
    def from_orm_model(cls, model: ProductQuantityPricing) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            product_id=model.product_id,
            quantity_low=model.quantity_low,
            quantity_high=model.quantity_high,
            unit_price=model.unit_price,
        )
