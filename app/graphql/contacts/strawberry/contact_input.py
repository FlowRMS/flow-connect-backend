from uuid import UUID

import strawberry
from commons.db.v6.crm.contact_model import Contact

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ContactInput(BaseInputGQL[Contact]):
    """GraphQL input type for creating/updating contacts."""

    first_name: str
    last_name: str
    email: str | None = strawberry.UNSET
    phone: str | None = strawberry.UNSET
    role: str | None = strawberry.UNSET
    territory: str | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET
    notes: str | None = strawberry.UNSET
    company_id: UUID | None = strawberry.UNSET
    external_id: str | None = strawberry.UNSET

    def to_orm_model(self) -> Contact:
        """Convert input to ORM model."""
        return Contact(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.optional_field(self.email),
            phone=self.optional_field(self.phone),
            role=self.optional_field(self.role),
            territory=self.optional_field(self.territory),
            tags=self.optional_field(self.tags),
            notes=self.optional_field(self.notes),
            external_id=self.optional_field(self.external_id),
        )
