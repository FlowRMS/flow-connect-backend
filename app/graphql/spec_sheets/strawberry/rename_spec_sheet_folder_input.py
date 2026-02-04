from uuid import UUID

import strawberry


@strawberry.input
class RenameSpecSheetFolderInput:
    """Input for renaming a spec sheet folder."""

    factory_id: UUID
    folder_id: UUID  # ID of the folder to rename
    new_name: str  # New name for the folder
