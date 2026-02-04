from decimal import Decimal

import strawberry
from commons.db.v6.warehouse import FreightCategory

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class FreightCategoryInput(BaseInputGQL[FreightCategory]):
    freight_class: Decimal
    description: str | None = None
    is_active: bool = True
    position: int | None = None

    def to_orm_model(self) -> FreightCategory:
        return FreightCategory(
            freight_class=self.freight_class,
            description=self.description,
            is_active=self.is_active,
            position=self.position or 0,
        )
