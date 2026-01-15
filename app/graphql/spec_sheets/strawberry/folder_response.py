"""GraphQL response type for Folder."""

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.spec_sheets import SpecSheetFolder

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class SpecSheetFolderResponse(DTOMixin[SpecSheetFolder]):
    """Response type for SpecSheetFolder."""

    _instance: strawberry.Private[SpecSheetFolder]
    id: UUID
    factory_id: UUID
    folder_path: str
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: SpecSheetFolder) -> Self:
        """Convert ORM model to GraphQL response."""
        return cls(
            _instance=model,
            id=model.id,
            factory_id=model.factory_id,
            folder_path=model.folder_path,
            created_at=model.created_at,
        )


@strawberry.type
class RenameSpecSheetFolderResult:
    """Result of renaming a folder."""

    folder: SpecSheetFolderResponse
    spec_sheets_updated: int
