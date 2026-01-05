from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.products.product_cpn import ProductCpn

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ProductCpnLiteInput(BaseInputGQL[ProductCpn]):
    customer_id: UUID
    customer_part_number: str
    unit_price: Decimal
    commission_rate: Decimal

    def to_orm_model(self) -> ProductCpn:
        return ProductCpn(
            customer_id=self.customer_id,
            customer_part_number=self.customer_part_number,
            unit_price=self.unit_price,
            commission_rate=self.commission_rate,
        )


@strawberry.input
class ProductCpnInput(BaseInputGQL[ProductCpn]):
    product_id: UUID
    customer_id: UUID
    customer_part_number: str
    unit_price: Decimal
    commission_rate: Decimal

    def to_orm_model(self) -> ProductCpn:
        cpn = ProductCpn(
            customer_id=self.customer_id,
            customer_part_number=self.customer_part_number,
            unit_price=self.unit_price,
            commission_rate=self.commission_rate,
        )
        cpn.product_id = self.product_id
        return cpn
