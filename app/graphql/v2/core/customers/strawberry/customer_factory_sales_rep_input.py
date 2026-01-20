from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.core.customers.customer_factory_sales_rep import (
    CustomerFactorySalesRep,
)

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CustomerFactorySalesRepInput(BaseInputGQL[CustomerFactorySalesRep]):
    customer_id: UUID
    factory_id: UUID
    user_id: UUID
    rate: Decimal
    position: int = 0

    def to_orm_model(self) -> CustomerFactorySalesRep:
        return CustomerFactorySalesRep(
            customer_id=self.customer_id,
            factory_id=self.factory_id,
            user_id=self.user_id,
            rate=self.rate,
            position=self.position,
        )


@strawberry.input
class SalesRepSplitInput:
    user_id: UUID
    rate: Decimal
    position: int = 0


@strawberry.input
class CustomerFactorySalesRepBulkInput:
    customer_id: UUID
    factory_id: UUID
    splits: list[SalesRepSplitInput]

    def to_orm_models(self) -> list[CustomerFactorySalesRep]:
        return [
            CustomerFactorySalesRep(
                customer_id=self.customer_id,
                factory_id=self.factory_id,
                user_id=split.user_id,
                rate=split.rate,
                position=split.position,
            )
            for split in self.splits
        ]
