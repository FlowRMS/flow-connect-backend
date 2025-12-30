import decimal

import strawberry
from commons.db.v6.core.products.product_uom import ProductUom

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ProductUomInput(BaseInputGQL[ProductUom]):
    title: str
    division_factor: decimal.Decimal | None = None
    description: str | None = None

    def to_orm_model(self) -> ProductUom:
        return ProductUom(
            title=self.title,
            division_factor=self.division_factor,
            description=self.description,
        )
