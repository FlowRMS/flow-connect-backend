"""GraphQL input type for moving a folder."""

from uuid import UUID

import strawberry


@strawberry.input
class MoveFolderInput:
    """Input for moving a folder to a new location."""

    manufacturer_id: UUID
    old_folder_path: str  # Current path like "Folder1/Folder2"
    new_folder_path: str  # New path like "Folder3" or empty string for root
