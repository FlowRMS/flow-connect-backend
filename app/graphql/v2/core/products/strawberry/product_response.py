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
    default_commission_rate: Decimal
    published: bool
    approval_needed: bool | None
    description: str | None

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
        )


@strawberry.type
class ProductResponse(ProductLiteResponse):
    @strawberry.field
    async def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(
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
