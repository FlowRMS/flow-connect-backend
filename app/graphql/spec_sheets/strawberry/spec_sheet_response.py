"""GraphQL response type for SpecSheet."""

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.spec_sheets.models.spec_sheet_model import SpecSheet


@strawberry.type
class SpecSheetResponse(DTOMixin[SpecSheet]):
    """Response type for SpecSheet."""

    id: UUID
    manufacturer_id: UUID
    file_name: str
    display_name: str
    upload_source: str
    source_url: str | None
    file_url: str
    file_size: int
    page_count: int
    categories: list[str]
    tags: list[str] | None
    needs_review: bool
    published: bool
    usage_count: int
    highlight_count: int
    created_at: datetime
    created_by: str

    @classmethod
    def from_orm_model(cls, model: SpecSheet) -> Self:
        """Convert ORM model to GraphQL response."""
        # Handle created_by User object
        created_by_str = ""
        if hasattr(model, "created_by") and model.created_by:
            if hasattr(model.created_by, "full_name"):
                created_by_str = model.created_by.full_name or ""
            elif hasattr(model.created_by, "email"):
                created_by_str = model.created_by.email or ""

        return cls(
            id=model.id,
            manufacturer_id=model.manufacturer_id,
            file_name=model.file_name,
            display_name=model.display_name,
            upload_source=model.upload_source,
            source_url=model.source_url,
            file_url=model.file_url,
            file_size=model.file_size,
            page_count=model.page_count,
            categories=model.categories,
            tags=model.tags,
            needs_review=model.needs_review,
            published=model.published,
            usage_count=model.usage_count,
            highlight_count=model.highlight_count,
            created_at=model.created_at,
            created_by=created_by_str,
        )
