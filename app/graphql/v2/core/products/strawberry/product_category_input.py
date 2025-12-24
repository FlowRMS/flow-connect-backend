from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product_category import ProductCategory

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ProductCategoryInput(BaseInputGQL[ProductCategory]):
    title: str
    commission_rate: Decimal
    factory_id: UUID | None = None
    parent_id: UUID | None = None
    grandparent_id: UUID | None = None

    def to_orm_model(self) -> ProductCategory:
        return ProductCategory(
            title=self.title,
            factory_id=self.factory_id,
            commission_rate=self.commission_rate,
            parent_id=self.parent_id,
            grandparent_id=self.grandparent_id,
        )
