from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product_category import ProductCategory

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ProductCategoryLiteResponse(DTOMixin[ProductCategory]):
    _instance: strawberry.Private[ProductCategory]
    id: UUID
    title: str
    factory_id: UUID | None
    commission_rate: Decimal | None

    @classmethod
    def from_orm_model(cls, model: ProductCategory) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            title=model.title,
            factory_id=model.factory_id,
            commission_rate=model.commission_rate,
        )


@strawberry.type
class ProductCategoryResponse(ProductCategoryLiteResponse):
    @strawberry.field
    def parent(
        self,
    ) -> ProductCategoryLiteResponse | None:
        if self._instance.parent is None:
            return None

        return ProductCategoryLiteResponse.from_orm_model(self._instance.parent)

    @strawberry.field
    def grandparent(
        self,
    ) -> ProductCategoryLiteResponse | None:
        if self._instance.grandparent is None:
            return None

        return ProductCategoryLiteResponse.from_orm_model(self._instance.grandparent)

    @strawberry.field
    def children(
        self,
    ) -> list[ProductCategoryLiteResponse]:
        """Get direct children of this category (where parent_id = self.id)."""
        return ProductCategoryLiteResponse.from_orm_model_list(self._instance.children)
