from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.companies.company_model import Company
from commons.db.v6.crm.companies.company_type import CompanyType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse

if TYPE_CHECKING:
    from app.graphql.v2.core.territories.strawberry.territory_response import (
        TerritoryLiteResponse,
    )


@strawberry.type
class CompanyLiteResponse(DTOMixin[Company]):
    _instance: strawberry.Private[Company]
    id: UUID
    created_at: datetime
    name: str
    company_source_type: CompanyType
    website: str | None
    phone: str | None
    tags: list[str] | None
    parent_company_id: UUID | None
    territory_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Company) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            name=model.name,
            company_source_type=model.company_source_type,
            website=model.website,
            phone=model.phone,
            tags=model.tags,
            parent_company_id=model.parent_company_id,
            territory_id=model.territory_id,
        )


@strawberry.type
class CompanyResponse(CompanyLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def territory(self) -> TerritoryLiteResponse | None:
        from app.graphql.v2.core.territories.strawberry.territory_response import (
            TerritoryLiteResponse,
        )

        territory = self._instance.territory
        if not territory:
            return None
        return TerritoryLiteResponse.from_orm_model(territory)
