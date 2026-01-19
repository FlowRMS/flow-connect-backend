from uuid import UUID

import strawberry
from commons.db.v6 import Organization

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class OrganizationInput(BaseInputGQL[Organization]):
    company_name: str
    street_address: str
    city: str
    state: str
    zip_code: str
    email_address: str
    phone_number: str
    address_line_2: str | None = strawberry.UNSET
    logo_file_id: UUID | None = strawberry.UNSET
    logo_width: int | None = strawberry.UNSET
    logo_height: int | None = strawberry.UNSET

    def to_orm_model(self) -> Organization:
        return Organization(
            company_name=self.company_name,
            street_address=self.street_address,
            city=self.city,
            state=self.state,
            zip_code=self.zip_code,
            email_address=self.email_address,
            phone_number=self.phone_number,
            address_line_2=self.optional_field(self.address_line_2),
            logo_file_id=self.optional_field(self.logo_file_id),
            logo_width=self.optional_field(self.logo_width) or 100,
            logo_height=self.optional_field(self.logo_height) or 100,
        )
