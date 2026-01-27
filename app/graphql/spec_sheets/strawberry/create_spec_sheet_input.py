"""GraphQL input type for creating a SpecSheet."""

from uuid import UUID

import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class CreateSpecSheetInput:
    """Input for creating a new spec sheet."""

    factory_id: UUID
    file_name: str
    display_name: str | None = None
    upload_source: str  # 'url' or 'file'
    source_url: str | None = None
    page_count: int = 1
    categories: list[str]
    tags: list[str] | None = None
    folder_id: UUID | None = None  # pyfiles.folders ID for folder organization
    needs_review: bool = False
    published: bool = True
    file: Upload | None = None  # File upload field for 'file' upload_source
