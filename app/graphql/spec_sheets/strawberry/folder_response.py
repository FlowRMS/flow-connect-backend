"""GraphQL response type for Folder."""

import uuid
from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.spec_sheets import SpecSheetFolder

from app.core.db.adapters.dto import DTOMixin

# Namespace UUID for generating deterministic folder IDs
FOLDER_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


@strawberry.type
class SpecSheetFolderResponse(DTOMixin[SpecSheetFolder]):
    """Response type for SpecSheetFolder."""

    _instance: strawberry.Private[SpecSheetFolder | None]
    id: UUID
    factory_id: UUID
    folder_path: str
    created_at: datetime | None
    spec_sheet_count: int

    @classmethod
    def from_orm_model(cls, model: SpecSheetFolder, spec_sheet_count: int = 0) -> Self:
        """Convert ORM model to GraphQL response."""
        return cls(
            _instance=model,
            id=model.id,
            factory_id=model.factory_id,
            folder_path=model.folder_path,
            created_at=model.created_at,
            spec_sheet_count=spec_sheet_count,
        )

    @classmethod
    def from_path(
        cls, factory_id: UUID, folder_path: str, spec_sheet_count: int
    ) -> Self:
        """Create response from folder path (virtual folder without DB record)."""
        # Generate deterministic UUID from factory_id + folder_path
        unique_key = f"{factory_id}:{folder_path}"
        virtual_id = uuid.uuid5(FOLDER_NAMESPACE, unique_key)
        return cls(
            _instance=None,
            id=virtual_id,
            factory_id=factory_id,
            folder_path=folder_path,
            created_at=None,
            spec_sheet_count=spec_sheet_count,
        )


@strawberry.type
class RenameSpecSheetFolderResult:
    """Result of renaming a folder."""

    folder: SpecSheetFolderResponse
    spec_sheets_updated: int


@strawberry.type
class FolderPathWithCount:
    """Simple folder path with spec sheet count for tree view."""

    folder_path: str
    spec_sheet_count: int
