"""GraphQL input types for Folder operations using pyfiles.folders."""

from uuid import UUID

import strawberry


@strawberry.input
class CreateFolderInput:
    """Input for creating a new folder."""

    factory_id: UUID
    parent_folder_id: UUID | None = None  # Parent folder ID (None for root level)
    folder_name: str  # Name of the new folder


@strawberry.input
class RenameFolderInput:
    """Input for renaming a folder."""

    factory_id: UUID
    folder_id: UUID  # ID of the folder to rename
    new_name: str  # New name for the folder


@strawberry.input
class DeleteFolderInput:
    """Input for deleting a folder."""

    factory_id: UUID
    folder_id: UUID  # ID of the folder to delete


@strawberry.input
class MoveFolderInput:
    """Input for moving a folder to a new parent."""

    factory_id: UUID
    folder_id: UUID  # ID of the folder to move
    new_parent_id: UUID | None = None  # New parent folder ID (None for root)


@strawberry.input
class MoveSpecSheetToFolderInput:
    """Input for moving a spec sheet to a different folder."""

    spec_sheet_id: UUID
    folder_id: UUID | None = None  # Target folder ID (None for root/no folder)
