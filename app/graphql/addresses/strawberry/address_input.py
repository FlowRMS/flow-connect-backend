from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.addresses.models.address_model import CompanyAddress
from app.graphql.addresses.models.address_type import AddressType


@strawberry.input
class AddressInput(BaseInputGQL[CompanyAddress]):
    """GraphQL input type for creating/updating CompanyAddress entities."""

    company_id: UUID
    address_type: AddressType
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None

    def to_orm_model(self) -> CompanyAddress:
        return CompanyAddress(
            company_id=self.company_id,
            address_type=self.address_type,
            address_line_1=self.address_line_1,
            address_line_2=self.address_line_2,
            city=self.city,
            state=self.state,
            zip_code=self.zip_code,
        )
