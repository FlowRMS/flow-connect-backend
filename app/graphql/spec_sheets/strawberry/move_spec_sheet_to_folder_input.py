from uuid import UUID

import strawberry


@strawberry.input
class MoveSpecSheetToFolderInput:
    """Input for moving a spec sheet to a different folder."""

    spec_sheet_id: UUID
    folder_id: UUID | None = None  # Target folder ID (None for root/no folder)
