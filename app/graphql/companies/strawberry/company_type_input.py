from uuid import UUID

import strawberry
from commons.db.v6.crm.companies import CompanyTypeEntity

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CompanyTypeInput(BaseInputGQL[CompanyTypeEntity]):
    id: UUID | None = None
    name: str
    display_order: int = 0

    def to_orm_model(self) -> CompanyTypeEntity:
        return CompanyTypeEntity(
            name=self.name,
            display_order=self.display_order,
            is_active=True,
        )
