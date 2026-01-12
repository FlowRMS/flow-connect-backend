from datetime import date
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product import Product

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_category_response import (
    ProductCategoryResponse,
)
from app.graphql.v2.core.products.strawberry.product_uom_response import (
    ProductUomResponse,
)


@strawberry.type
class ProductLiteResponse(DTOMixin[Product]):
    _instance: strawberry.Private[Product]
    id: UUID
    factory_part_number: str
    unit_price: Decimal
    default_commission_rate: Decimal | None
    published: bool
    approval_needed: bool | None
    description: str | None
    upc: str | None
    default_divisor: Decimal | None
    min_order_qty: Decimal | None
    lead_time: int | None
    unit_price_discount_rate: Decimal | None
    commission_discount_rate: Decimal | None
    approval_date: date | None
    approval_comments: str | None
    tags: list[str] | None

    @classmethod
    def from_orm_model(cls, model: Product) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            factory_part_number=model.factory_part_number,
            unit_price=model.unit_price,
            default_commission_rate=model.default_commission_rate,
            published=model.published,
            approval_needed=model.approval_needed,
            description=model.description,
            upc=model.upc,
            default_divisor=model.default_divisor,
            min_order_qty=model.min_order_qty,
            lead_time=model.lead_time,
            unit_price_discount_rate=model.unit_price_discount_rate,
            commission_discount_rate=model.commission_discount_rate,
            approval_date=model.approval_date,
            approval_comments=model.approval_comments,
            tags=model.tags,
        )




@strawberry.type
class ProductResponse(ProductLiteResponse):
    @strawberry.field   
    async def factory(self) -> FactoryLiteResponse | None:
        factory = await self._instance.awaitable_attrs.factory
        if not factory:
            return None
        return FactoryLiteResponse.from_orm_model(factory)
    
    @strawberry.field
    def category(self) -> ProductCategoryResponse | None:
        return ProductCategoryResponse.from_orm_model_optional(self._instance.category)

    @strawberry.field
    def uom(self) -> ProductUomResponse | None:
        return ProductUomResponse.from_orm_model_optional(self._instance.uom)
