from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import Customer

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.customers.strawberry.customer_split_rate_response import (
    CustomerSplitRateResponse,
)
from app.graphql.v2.core.territories.strawberry.territory_response import (
    TerritoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class CustomerLiteResponse(DTOMixin[Customer]):
    _instance: strawberry.Private[Customer]
    id: UUID
    company_name: str
    published: bool
    is_parent: bool
    parent_id: UUID | None
    buying_group_id: UUID | None
    territory_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Customer) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            company_name=model.company_name,
            published=model.published,
            is_parent=model.is_parent,
            parent_id=model.parent_id,
            buying_group_id=model.buying_group_id,
            territory_id=model.territory_id,
        )


@strawberry.type
class CustomerResponse(CustomerLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def outside_reps(self) -> list[CustomerSplitRateResponse]:
        return CustomerSplitRateResponse.from_orm_model_list(
            self._instance.outside_reps
        )

    @strawberry.field
    def inside_reps(self) -> list[CustomerSplitRateResponse]:
        return CustomerSplitRateResponse.from_orm_model_list(self._instance.inside_reps)

    @strawberry.field
    def parent(self) -> CustomerLiteResponse | None:
        parent = self._instance.parent
        if not parent:
            return None
        return CustomerLiteResponse.from_orm_model(parent)

    @strawberry.field
    def buying_group(self) -> CustomerLiteResponse | None:
        buying_group = self._instance.buying_group
        if not buying_group:
            return None
        return CustomerLiteResponse.from_orm_model(buying_group)

    @strawberry.field
    def territory(self) -> TerritoryLiteResponse | None:
        return TerritoryLiteResponse.from_orm_model_optional(self._instance.territory)
