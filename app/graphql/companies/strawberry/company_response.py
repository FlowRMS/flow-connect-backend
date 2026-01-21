from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.companies.company_model import Company

from app.core.db.adapters.dto import DTOMixin
from app.graphql.companies.strawberry.company_type_response import (
    CompanyTypeResponse,
)
from app.graphql.v2.core.territories.strawberry.territory_response import (
    TerritoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class CompanyLiteResponse(DTOMixin[Company]):
    _instance: strawberry.Private[Company]
    id: UUID
    created_at: datetime
    name: str
    company_type_id: UUID | None
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
            company_type_id=model.company_type_id,
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
        return TerritoryLiteResponse.from_orm_model_optional(self._instance.territory)

    @strawberry.field
    def company_type(
        self,
    ) -> CompanyTypeResponse | None:
        return CompanyTypeResponse.from_orm_model_optional(self._instance.company_type)
