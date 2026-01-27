import uuid
from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.spec_sheets import SpecSheetFolder
from commons.db.v6.files import Folder

from app.core.db.adapters.dto import DTOMixin

# Namespace UUID for generating deterministic folder IDs
FOLDER_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


@strawberry.type
class SpecSheetFolderResponse(DTOMixin[SpecSheetFolder]):
    """Response type for SpecSheetFolder."""

    _instance: strawberry.Private[SpecSheetFolder | Folder | None]
    _pyfiles_folder: strawberry.Private[Folder | None] = None
    id: UUID
    factory_id: UUID
    folder_path: str
    created_at: datetime | None
    spec_sheet_count: int

    @strawberry.field
    def name(self) -> str:
        """Get folder name."""
        # For pyfiles folders, use the folder's name directly
        if self._pyfiles_folder is not None:
            return self._pyfiles_folder.name
        # For path-based folders, derive name from the path
        if not self.folder_path:
            return ""
        return self.folder_path.split("/")[-1]

    @strawberry.field
    def parent_id(self) -> UUID | None:
        """Get parent folder ID."""
        # For pyfiles folders, use the stored parent_id (which could be None for root)
        if self._pyfiles_folder is not None:
            return self._pyfiles_folder.parent_id
        # For path-based folders, derive parent_id from the path
        if not self.folder_path or "/" not in self.folder_path:
            return None
        parent_path = "/".join(self.folder_path.split("/")[:-1])
        if not parent_path:
            return None
        unique_key = f"{self.factory_id}:{parent_path}"
        return uuid.uuid5(FOLDER_NAMESPACE, unique_key)

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
    def from_pyfiles_folder(
        cls, folder: Folder, factory_id: UUID, spec_sheet_count: int = 0
    ) -> Self:
        """Convert pyfiles.Folder to GraphQL response."""
        return cls(
            _instance=folder,
            _pyfiles_folder=folder,
            id=folder.id,
            factory_id=factory_id,
            folder_path=folder.name,  # For pyfiles, folder_path is just the name
            created_at=folder.created_at,
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
