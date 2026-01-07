from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.files import Folder

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.v2.files.strawberry.file_response import FileLiteResponse


@strawberry.type
class FolderLiteResponse(DTOMixin[Folder]):
    _instance: strawberry.Private[Folder]
    id: UUID
    created_at: datetime
    name: str
    description: str | None
    parent_id: UUID | None
    archived: bool

    @classmethod
    def from_orm_model(cls, model: Folder) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
            archived=model.archived,
        )


@strawberry.type
class FolderResponse(FolderLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)


@strawberry.type
class FolderWithChildrenResponse(FolderResponse):
    @strawberry.field
    def children(self) -> list[FolderLiteResponse]:
        return FolderLiteResponse.from_orm_model_list(self._instance.children)

    @strawberry.field
    def files(self) -> list[FileLiteResponse]:
        return FileLiteResponse.from_orm_model_list(self._instance.files)

    @strawberry.field
    def parent(self) -> FolderLiteResponse | None:
        if self._instance.parent is None:
            return None
        return FolderLiteResponse.from_orm_model(self._instance.parent)
