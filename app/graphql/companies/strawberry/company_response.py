from datetime import datetime
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.companies.models.company_model import Company
from app.graphql.companies.models.company_type import CompanyType


@strawberry.type
class CompanyResponse(DTOMixin[Company]):
    """GraphQL type for Company entity (output/query results)."""

    id: UUID
    entry_date: datetime
    created_by: UUID
    name: str
    company_source_type: CompanyType
    website: str | None
    phone: str | None
    tags: list[str] | None
    parent_company_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Company) -> "CompanyResponse":
        """Convert ORM model to GraphQL type."""
        return cls(
            id=model.id,
            entry_date=model.entry_date,
            created_by=model.created_by,
            name=model.name,
            company_source_type=model.company_source_type,
            website=model.website,
            phone=model.phone,
            tags=model.tags,
            parent_company_id=model.parent_company_id,
        )
