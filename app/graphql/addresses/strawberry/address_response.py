import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core.addresses.address import (
    Address,
    AddressSourceTypeEnum,
    AddressTypeEnum,
)

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class AddressResponse(DTOMixin[Address]):
    _instance: strawberry.Private[Address]
    id: UUID
    created_at: datetime.datetime
    source_id: UUID
    source_type: AddressSourceTypeEnum
    address_type: AddressTypeEnum
    line_1: str
    line_2: str | None
    city: str
    state: str | None
    zip_code: str | None
    country: str
    notes: str | None
    is_primary: bool

    @classmethod
    def from_orm_model(cls, model: Address) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            source_id=model.source_id,
            source_type=model.source_type,
            address_type=model.address_type,
            line_1=model.line_1,
            line_2=model.line_2,
            city=model.city,
            state=model.state,
            zip_code=model.zip_code,
            country=model.country,
            notes=model.notes,
            is_primary=model.is_primary,
        )
