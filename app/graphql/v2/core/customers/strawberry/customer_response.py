from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import Customer

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.customers.strawberry.customer_split_rate_response import (
    CustomerSplitRateResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class CustomerResponse(DTOMixin[Customer]):
    _instance: strawberry.Private[Customer]
    id: UUID
    company_name: str
    published: bool
    is_parent: bool
    parent_id: UUID | None
    contact_email: str | None
    contact_number: str | None

    @classmethod
    def from_orm_model(cls, model: Customer) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            company_name=model.company_name,
            published=model.published,
            is_parent=model.is_parent,
            parent_id=model.parent_id,
            contact_email=model.contact_email,
            contact_number=model.contact_number,
        )

    @strawberry.field
    async def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(
            await self._instance.awaitable_attrs.created_by
        )

    @strawberry.field
    async def outside_reps(self) -> list[CustomerSplitRateResponse]:
        return CustomerSplitRateResponse.from_orm_model_list(
            self._instance.outside_reps
        )

    @strawberry.field
    async def inside_reps(self) -> list[CustomerSplitRateResponse]:
        return CustomerSplitRateResponse.from_orm_model_list(self._instance.inside_reps)
