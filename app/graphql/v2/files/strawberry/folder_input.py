from uuid import UUID

import strawberry


@strawberry.input
class CreateFolderInput:
    name: str
    description: str | None = None
    parent_id: UUID | None = None


@strawberry.input
class UpdateFolderInput:
    folder_id: UUID
    name: str | None = None
    description: str | None = None
    parent_id: UUID | None = None
