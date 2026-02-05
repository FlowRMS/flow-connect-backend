from uuid import UUID

import strawberry
from commons.db.v6.core.customers.factory_customer_reference import (
    FactoryCustomerReference,
)

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class FactoryCustomerReferenceInput(BaseInputGQL[FactoryCustomerReference]):
    factory_id: UUID
    customer_id: UUID
    reference_number: str
    address_id: UUID | None = None

    def to_orm_model(self) -> FactoryCustomerReference:
        return FactoryCustomerReference(
            factory_id=self.factory_id,
            customer_id=self.customer_id,
            reference_number=self.reference_number,
            address_id=self.address_id,
        )
