from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product_quantity_pricing import ProductQuantityPricing

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ProductQuantityPricingInput(BaseInputGQL[ProductQuantityPricing]):
    product_id: UUID
    quantity_low: Decimal
    quantity_high: Decimal
    unit_price: Decimal

    def to_orm_model(self) -> ProductQuantityPricing:
        return ProductQuantityPricing(
            product_id=self.product_id,
            quantity_low=self.quantity_low,
            quantity_high=self.quantity_high,
            unit_price=self.unit_price,
        )
