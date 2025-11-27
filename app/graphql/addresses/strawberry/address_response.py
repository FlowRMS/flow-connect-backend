from datetime import datetime
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.addresses.models.address_model import Address
from app.graphql.addresses.models.address_type import AddressType


@strawberry.type
class AddressResponse(DTOMixin[Address]):
    """GraphQL type for Address entity (output/query results)."""

    id: UUID
    entry_date: datetime
    created_by: UUID
    company_id: UUID
    address_type: AddressType
    address_line_1: str | None
    address_line_2: str | None
    city: str | None
    state: str | None
    zip_code: str | None

    @classmethod
    def from_orm_model(cls, model: Address) -> "AddressResponse":
        """Convert ORM model to GraphQL type."""
        return cls(
            id=model.id,
            entry_date=model.entry_date,
            created_by=model.created_by,
            company_id=model.company_id,
            address_type=model.address_type,
            address_line_1=model.address_line_1,
            address_line_2=model.address_line_2,
            city=model.city,
            state=model.state,
            zip_code=model.zip_code,
        )
