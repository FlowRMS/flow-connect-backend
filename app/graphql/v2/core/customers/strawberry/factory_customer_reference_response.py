from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.customers.factory_customer_reference import (
    FactoryCustomerReference,
)

from app.core.db.adapters.dto import DTOMixin
from app.graphql.addresses.strawberry.address_response import AddressResponse
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)


@strawberry.type
class FactoryCustomerReferenceResponse(DTOMixin[FactoryCustomerReference]):
    _instance: strawberry.Private[FactoryCustomerReference]
    id: UUID
    factory_id: UUID
    customer_id: UUID
    reference_number: str
    address_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: FactoryCustomerReference) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            factory_id=model.factory_id,
            customer_id=model.customer_id,
            reference_number=model.reference_number,
            address_id=model.address_id,
        )

    @strawberry.field
    def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(self._instance.factory)

    @strawberry.field
    def customer(self) -> CustomerLiteResponse:
        return CustomerLiteResponse.from_orm_model(self._instance.customer)

    @strawberry.field
    def address(self) -> AddressResponse | None:
        address = self._instance.address
        if not address:
            return None
        return AddressResponse.from_orm_model(address)
