from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.models.core.product import Product as CoreProduct

from app.core.db.adapters.dto import DTOMixin
from app.graphql.core.factories.strawberry.factory_response import FactoryResponse
from app.graphql.core.products.models import ProductV2
from app.graphql.core.products.strawberry.product_category_response import (
    ProductCategoryResponse,
)
from app.graphql.core.products.strawberry.product_uom_response import ProductUomResponse


@strawberry.type
class ProductLiteResponse(DTOMixin[CoreProduct]):
    id: UUID
    factory_part_number: str
    factory_id: UUID

    @classmethod
    def from_orm_model(cls, model: CoreProduct) -> Self:
        return cls(
            id=model.id,
            factory_part_number=model.factory_part_number,
            factory_id=model.factory_id,
        )


@strawberry.type
class ProductResponse(DTOMixin[ProductV2]):
    _instance: strawberry.Private[ProductV2]
    id: UUID
    factory_part_number: str
    unit_price: Decimal
    default_commission_rate: Decimal
    published: bool
    approval_needed: bool | None
    description: str | None
    lead_time: str | None
    min_order_qty: int | None
    commission_discount_rate: Decimal | None
    overall_discount_rate: Decimal | None
    cost: Decimal | None
    individual_upc: str | None
    approval_comments: str | None
    logo_url: str | None
    sales_model: str | None
    payout_type: str | None

    @classmethod
    def from_orm_model(cls, model: ProductV2) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            factory_part_number=model.factory_part_number,
            unit_price=model.unit_price,
            default_commission_rate=model.default_commission_rate,
            published=model.published,
            approval_needed=model.approval_needed,
            description=model.description,
            lead_time=model.lead_time,
            min_order_qty=model.min_order_qty,
            commission_discount_rate=model.commission_discount_rate,
            overall_discount_rate=model.overall_discount_rate,
            cost=model.cost,
            individual_upc=model.individual_upc,
            approval_comments=model.approval_comments,
            logo_url=model.logo_url,
            sales_model=model.sales_model,
            payout_type=model.payout_type,
        )

    @strawberry.field
    async def factory(self) -> FactoryResponse:
        return FactoryResponse.from_orm_model(
            await self._instance.awaitable_attrs.factory
        )

    @strawberry.field
    async def category(self) -> ProductCategoryResponse | None:
        if self._instance.category is None:
            return None

        return ProductCategoryResponse.from_orm_model(
            await self._instance.awaitable_attrs.category
        )

    @strawberry.field
    async def uom(self) -> ProductUomResponse | None:
        if self._instance.uom is None:
            return None

        return ProductUomResponse.from_orm_model(
            await self._instance.awaitable_attrs.uom
        )
