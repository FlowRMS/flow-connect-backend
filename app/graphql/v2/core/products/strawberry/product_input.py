from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product import Product

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ProductInput(BaseInputGQL[Product]):
    factory_part_number: str
    factory_id: UUID
    unit_price: Decimal
    default_commission_rate: Decimal
    product_category_id: UUID
    product_uom_id: UUID
    approval_needed: bool
    published: bool = False
    description: str | None = None
    lead_time: str | None = None
    min_order_qty: int | None = None
    commission_discount_rate: Decimal | None = None
    overall_discount_rate: Decimal | None = None
    cost: Decimal | None = None
    individual_upc: str | None = None
    approval_comments: str | None = None
    logo_url: str | None = None
    sales_model: str | None = None
    payout_type: str | None = None

    def to_orm_model(self) -> Product:
        return Product(
            factory_part_number=self.factory_part_number,
            factory_id=self.factory_id,
            product_category_id=self.product_category_id,
            product_uom_id=self.product_uom_id,
            unit_price=self.unit_price,
            default_commission_rate=self.default_commission_rate,
            published=self.published,
            approval_needed=self.approval_needed,
            description=self.description,
        )
