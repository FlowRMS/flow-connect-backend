from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.contact_model import Contact

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ContactLiteResponse(DTOMixin[Contact]):
    id: UUID
    created_at: datetime
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    role: str | None
    role_detail: str | None
    territory: str | None
    tags: list[str] | None
    notes: str | None
    external_id: str | None

    @classmethod
    def from_orm_model(cls, model: Contact) -> Self:
        return cls(
            id=model.id,
            created_at=model.created_at,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            role=model.role,
            role_detail=model.role_detail,
            territory=model.territory,
            tags=model.tags,
            notes=model.notes,
            external_id=model.external_id,
        )


@strawberry.type
class ContactResponse(ContactLiteResponse):
    pass
