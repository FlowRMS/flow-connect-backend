from uuid import UUID

import strawberry


@strawberry.input
class DeleteSpecSheetFolderInput:
    """Input for deleting a spec sheet folder."""

    factory_id: UUID
    folder_id: UUID  # ID of the folder to delete
