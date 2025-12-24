import strawberry
from commons.db.v6.core.products.product_uom import ProductUom

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ProductUomInput(BaseInputGQL[ProductUom]):
    title: str
    multiply: bool
    multiply_by: int
    description: str | None = None

    def to_orm_model(self) -> ProductUom:
        return ProductUom(
            title=self.title,
            multiply=self.multiply,
            multiply_by=self.multiply_by,
            description=self.description,
        )
