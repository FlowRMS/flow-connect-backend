"""GraphQL input types for Folder operations."""

from uuid import UUID

import strawberry


@strawberry.input
class CreateFolderInput:
    """Input for creating a new folder."""

    factory_id: UUID
    parent_path: str  # Parent folder path (empty string for root level)
    folder_name: str  # Name of the new folder


@strawberry.input
class RenameFolderInput:
    """Input for renaming a folder."""

    factory_id: UUID
    folder_path: str  # Current full path like "Folder1/Folder2"
    new_name: str  # New name for the folder (just the name, not full path)


@strawberry.input
class DeleteFolderInput:
    """Input for deleting a folder."""

    factory_id: UUID
    folder_path: str  # Full path of the folder to delete
