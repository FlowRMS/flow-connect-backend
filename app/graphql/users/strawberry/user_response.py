"""GraphQL response type for User."""

from typing import Self
from uuid import UUID

import strawberry
from commons.db.models import User

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class UserResponse(DTOMixin[User]):
    """GraphQL type for User entity (output/query results)."""

    id: UUID
    first_name: str
    last_name: str
    email: str
    full_name: str
    is_inside: bool | None
    is_outside: bool | None

    @classmethod
    def from_orm_model(cls, model: User) -> Self:
        """Convert ORM model to GraphQL type."""
        return cls(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            full_name=model.full_name,
            is_inside=model.inside,
            is_outside=model.outside,
        )
