from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.core import Factory

from app.core.db.adapters.dto import DTOMixin
from app.graphql.users.strawberry.user_response import UserResponse


@strawberry.type
class FactoryResponse(DTOMixin[Factory]):
    _instance: strawberry.Private[Factory]
    id: UUID
    title: str
    published: bool
    freight_discount_type: int

    @classmethod
    def from_orm_model(cls, model: Factory) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            title=model.title,
            published=model.published,
            freight_discount_type=model.freight_discount_type,
        )

    @strawberry.field
    async def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(
            await self._instance.awaitable_attrs.created_by
        )
