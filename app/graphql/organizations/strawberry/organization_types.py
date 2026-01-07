from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import Organization

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class OrganizationType(DTOMixin[Organization]):
    id: UUID
    company_name: str
    street_address: str
    address_line_2: str | None
    city: str
    state: str
    zip_code: str
    email_address: str
    phone_number: str
    logo_file_id: UUID | None
    logo_width: int
    logo_height: int

    @classmethod
    def from_orm_model(cls, model: Organization) -> Self:
        return cls(
            id=model.id,
            company_name=model.company_name,
            street_address=model.street_address,
            address_line_2=model.address_line_2,
            city=model.city,
            state=model.state,
            zip_code=model.zip_code,
            email_address=model.email_address,
            phone_number=model.phone_number,
            logo_file_id=model.logo_file_id,
            logo_width=model.logo_width,
            logo_height=model.logo_height,
        )
