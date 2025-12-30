from uuid import UUID

import strawberry
from commons.db.v6.core.addresses.address import (
    Address,
    AddressSourceTypeEnum,
    AddressTypeEnum,
)

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class AddressInput(BaseInputGQL[Address]):
    source_id: UUID
    source_type: AddressSourceTypeEnum
    address_type: AddressTypeEnum = AddressTypeEnum.OTHER
    line_1: str
    city: str
    country: str
    line_2: str | None = None
    state: str | None = None
    zip_code: str | None = None
    notes: str | None = None
    is_primary: bool = False

    def to_orm_model(self) -> Address:
        return Address(
            source_id=self.source_id,
            source_type=self.source_type,
            address_type=self.address_type,
            line_1=self.line_1,
            line_2=self.line_2,
            city=self.city,
            state=self.state,
            zip_code=self.zip_code,
            country=self.country,
            notes=self.notes,
            is_primary=self.is_primary,
        )
