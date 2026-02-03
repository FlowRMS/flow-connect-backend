from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.files import Folder


@strawberry.type
class SpecSheetFolderResponse:
    """Response type for spec sheet folders (using pyfiles.Folder)."""

    id: UUID
    factory_id: UUID
    name: str
    parent_id: UUID | None
    created_at: datetime | None
    spec_sheet_count: int

    @classmethod
    def from_folder(
        cls,
        folder: Folder,
        factory_id: UUID,
        spec_sheet_count: int = 0,
    ) -> Self:
        """Convert pyfiles.Folder to GraphQL response.

        Args:
            folder: The pyfiles.Folder model
            factory_id: The factory this folder belongs to
            spec_sheet_count: Number of spec sheets in this folder
        """
        return cls(
            id=folder.id,
            factory_id=factory_id,
            name=folder.name,
            parent_id=folder.parent_id,
            created_at=folder.created_at,
            spec_sheet_count=spec_sheet_count,
        )


@strawberry.type
class FolderWithChildrenResponse(SpecSheetFolderResponse):
    """Folder response with children included."""

    children: list["SpecSheetFolderResponse"]

    @classmethod
    def from_folder_with_children(
        cls,
        folder: Folder,
        factory_id: UUID,
        children: list[tuple[Folder, int]],
        spec_sheet_count: int = 0,
    ) -> Self:
        """Convert folder with children to response."""
        return cls(
            id=folder.id,
            factory_id=factory_id,
            name=folder.name,
            parent_id=folder.parent_id,
            created_at=folder.created_at,
            spec_sheet_count=spec_sheet_count,
            children=[
                SpecSheetFolderResponse.from_folder(child, factory_id, count)
                for child, count in children
            ],
        )
