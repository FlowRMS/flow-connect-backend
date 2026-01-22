"""Lite response type for users - minimal fields for nested responses."""

from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.user import User

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class UserLiteResponse(DTOMixin[User]):
    """Lite response for users - used in nested relations."""

    _instance: strawberry.Private[User]
    id: UUID
    full_name: str
    email: str

    @classmethod
    def from_orm_model(cls, model: User) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            full_name=model.full_name,
            email=model.email,
        )
