"""GraphQL response types for SpecSheet Highlights."""

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.spec_sheets.models.spec_sheet_highlight_model import (
    SpecSheetHighlightRegion,
    SpecSheetHighlightVersion,
)


@strawberry.type
class HighlightRegionResponse(DTOMixin[SpecSheetHighlightRegion]):
    """Response type for a highlight region."""

    id: UUID
    version_id: UUID
    page_number: int
    x: float
    y: float
    width: float
    height: float
    shape_type: str
    color: str
    annotation: str | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: SpecSheetHighlightRegion) -> Self:
        """Convert ORM model to GraphQL response."""
        return cls(
            id=model.id,
            version_id=model.version_id,
            page_number=model.page_number,
            x=model.x,
            y=model.y,
            width=model.width,
            height=model.height,
            shape_type=model.shape_type,
            color=model.color,
            annotation=model.annotation,
            created_at=model.created_at,
        )


@strawberry.type
class HighlightVersionResponse(DTOMixin[SpecSheetHighlightVersion]):
    """Response type for a highlight version."""

    id: UUID
    spec_sheet_id: UUID
    name: str
    description: str | None
    version_number: int
    is_active: bool
    regions: list[HighlightRegionResponse]
    region_count: int
    created_at: datetime
    created_by: str

    @classmethod
    def from_orm_model(cls, model: SpecSheetHighlightVersion) -> Self:
        """Convert ORM model to GraphQL response."""
        # Handle created_by User object
        created_by_str = ""
        if model.created_by:
            created_by_str = model.created_by.full_name or model.created_by.email or ""

        # Convert regions
        regions = [HighlightRegionResponse.from_orm_model(r) for r in model.regions]

        return cls(
            id=model.id,
            spec_sheet_id=model.spec_sheet_id,
            name=model.name,
            description=model.description,
            version_number=model.version_number,
            is_active=model.is_active,
            regions=regions,
            region_count=len(regions),
            created_at=model.created_at,
            created_by=created_by_str,
        )
