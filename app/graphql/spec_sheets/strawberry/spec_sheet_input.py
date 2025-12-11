"""GraphQL input types for SpecSheet."""

from uuid import UUID

import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class CreateSpecSheetInput:
    """Input for creating a new spec sheet."""

    manufacturer_id: UUID
    file_name: str
    display_name: str | None = None
    upload_source: str  # 'url' or 'file'
    source_url: str | None = None
    file_url: str | None = None  # Made optional since it will be generated for file uploads
    file_size: int | None = None  # Made optional since it will be calculated for file uploads
    page_count: int = 1
    categories: list[str]
    tags: list[str] | None = None
    needs_review: bool = False
    published: bool = True
    file: Upload | None = None  # Added file upload field


@strawberry.input
class UpdateSpecSheetInput:
    """Input for updating an existing spec sheet."""

    display_name: str | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    needs_review: bool | None = None
    published: bool | None = None
