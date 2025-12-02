from datetime import datetime
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.contacts.models.contact_model import Contact


@strawberry.type
class ContactResponse(DTOMixin[Contact]):
    """GraphQL type for Contact entity (output/query results)."""

    id: UUID
    created_at: datetime
    # created_by: UUID
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    role: str | None
    territory: str | None
    tags: list[str] | None
    notes: str | None
    company_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Contact) -> "ContactResponse":
        """Convert ORM model to GraphQL type."""
        return cls(
            id=model.id,
            created_at=model.created_at,
            # created_by=model.created_by,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            role=model.role,
            territory=model.territory,
            tags=model.tags,
            notes=model.notes,
            company_id=model.company_id,
        )
