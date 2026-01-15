from uuid import UUID

import strawberry
from commons.db.v6.crm import CompanyType
from commons.db.v6.crm.companies.company_model import Company

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CompanyInput(BaseInputGQL[Company]):
    name: str
    company_source_type: CompanyType
    website: str | None = strawberry.UNSET
    phone: str | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET
    parent_company_id: UUID | None = strawberry.UNSET
    territory_id: UUID | None = strawberry.UNSET

    def to_orm_model(self) -> Company:
        return Company(
            name=self.name,
            company_source_type=self.company_source_type,
            website=self.optional_field(self.website),
            phone=self.optional_field(self.phone),
            tags=self.optional_field(self.tags),
            parent_company_id=self.optional_field(self.parent_company_id),
            territory_id=self.optional_field(self.territory_id),
        )
