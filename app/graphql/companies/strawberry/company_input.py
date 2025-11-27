from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.companies.models.company_model import Company
from app.graphql.companies.models.company_type import CompanyType


@strawberry.input
class CompanyInput(BaseInputGQL[Company]):
    """GraphQL input type for creating/updating companies."""

    name: str
    company_source_type: CompanyType
    website: str | None = strawberry.UNSET
    phone: str | None = strawberry.UNSET
    territory: str | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET
    parent_company_id: UUID | None = strawberry.UNSET

    def to_orm_model(self) -> Company:
        """Convert input to ORM model."""
        return Company(
            name=self.name,
            company_source_type=self.company_source_type,
            website=self.optional_field(self.website),
            phone=self.optional_field(self.phone),
            tags=self.optional_field(self.tags),
            parent_company_id=self.optional_field(self.parent_company_id),
        )
