from uuid import UUID

import strawberry


@strawberry.input
class CreateSpecSheetFolderInput:
    """Input for creating a new spec sheet folder."""

    factory_id: UUID
    parent_folder_id: UUID | None = None  # Parent folder ID (None for root level)
    folder_name: str  # Name of the new folder
