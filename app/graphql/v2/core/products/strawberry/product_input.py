from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product import Product

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.products.strawberry.product_cpn_input import (
    ProductCpnLiteInput,
)


@strawberry.input
class ProductInput(BaseInputGQL[Product]):
    factory_part_number: str
    factory_id: UUID
    unit_price: Decimal
    default_commission_rate: Decimal
    product_uom_id: UUID
    product_category_id: UUID | None = None
    approval_needed: bool | None = None
    published: bool = False
    description: str | None = None
    upc: str | None = None
    default_divisor: Decimal | None = None
    min_order_qty: Decimal | None = None
    lead_time: int | None = None
    unit_price_discount_rate: Decimal | None = None
    commission_discount_rate: Decimal | None = None
    approval_date: date | None = None
    approval_comments: str | None = None
    tags: list[str] | None = None
    cpns: list[ProductCpnLiteInput] | None = None

    def to_orm_model(self) -> Product:
        product_cpns = self.cpns or []
        product = Product(
            factory_part_number=self.factory_part_number,
            factory_id=self.factory_id,
            product_category_id=self.product_category_id,
            product_uom_id=self.product_uom_id,
            unit_price=self.unit_price,
            default_commission_rate=self.default_commission_rate,
            published=self.published,
            approval_needed=self.approval_needed,
            description=self.description,
            upc=self.upc,
            default_divisor=self.default_divisor,
            min_order_qty=self.min_order_qty,
            lead_time=self.lead_time,
            unit_price_discount_rate=self.unit_price_discount_rate,
            commission_discount_rate=self.commission_discount_rate,
            approval_date=self.approval_date,
            approval_comments=self.approval_comments,
            tags=self.tags,
            # product_cpns=[cpn.to_orm_model() for cpn in product_cpns],
        )
        if product_cpns:
            product.product_cpns = [cpn.to_orm_model() for cpn in product_cpns]
        return product
