from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.users.strawberry.user_response import UserResponse
from app.graphql.v2.core.customers.models import CustomerV2


@strawberry.type
class CustomerResponse(DTOMixin[CustomerV2]):
    _instance: strawberry.Private[CustomerV2]
    id: UUID
    company_name: str
    published: bool
    is_parent: bool
    parent_id: UUID | None
    contact_email: str | None
    contact_number: str | None
    customer_branch_id: UUID | None
    customer_territory_id: UUID | None
    logo_url: str | None
    # inside_rep_id: UUID | None
    type: str | None

    @classmethod
    def from_orm_model(cls, model: CustomerV2) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            company_name=model.company_name,
            published=model.published,
            is_parent=model.is_parent,
            parent_id=model.parent_id,
            contact_email=model.contact_email,
            contact_number=model.contact_number,
            customer_branch_id=model.customer_branch_id,
            customer_territory_id=model.customer_territory_id,
            logo_url=model.logo_url,
            type=model.type,
        )

    @strawberry.field
    async def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(
            await self._instance.awaitable_attrs.created_by
        )

    @strawberry.field
    async def inside_rep(self) -> UserResponse | None:
        return UserResponse.from_orm_model_optional(
            await self._instance.awaitable_attrs.inside_rep
        )
