from uuid import UUID

import strawberry


@strawberry.input
class MoveSpecSheetFolderInput:
    """Input for moving a spec sheet folder to a new parent."""

    factory_id: UUID
    folder_id: UUID  # ID of the folder to move
    new_parent_id: UUID | None = None  # New parent folder ID (None for root)
