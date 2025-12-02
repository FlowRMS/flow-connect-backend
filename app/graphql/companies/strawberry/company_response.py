from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.companies.models.company_model import Company
from app.graphql.companies.models.company_type import CompanyType
from app.graphql.users.strawberry.user_response import UserResponse


@strawberry.type
class CompanyResponse(DTOMixin[Company]):
    """GraphQL type for Company entity (output/query results)."""

    _instance: strawberry.Private[Company]
    id: UUID
    created_at: datetime
    name: str
    company_source_type: CompanyType
    website: str | None
    phone: str | None
    tags: list[str] | None
    parent_company_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Company) -> Self:
        """Convert ORM model to GraphQL type."""
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
        )

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)
