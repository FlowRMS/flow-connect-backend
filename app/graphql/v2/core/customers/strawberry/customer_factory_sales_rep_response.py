from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.customers.customer_factory_sales_rep import (
    CustomerFactorySalesRep,
)

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class CustomerFactorySalesRepResponse(DTOMixin[CustomerFactorySalesRep]):
    _instance: strawberry.Private[CustomerFactorySalesRep]
    id: UUID
    customer_id: UUID
    factory_id: UUID
    user_id: UUID
    rate: Decimal
    position: int

    @classmethod
    def from_orm_model(cls, model: CustomerFactorySalesRep) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            customer_id=model.customer_id,
            factory_id=model.factory_id,
            user_id=model.user_id,
            rate=model.rate,
            position=model.position,
        )

    @strawberry.field
    async def customer(self) -> CustomerLiteResponse:
        return CustomerLiteResponse.from_orm_model(
            await self._instance.awaitable_attrs.customer
        )

    @strawberry.field
    async def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(
            await self._instance.awaitable_attrs.factory
        )

    @strawberry.field
    async def user(self) -> UserResponse:
        return UserResponse.from_orm_model(await self._instance.awaitable_attrs.user)
