"""GraphQL Strawberry types for SpecSheets."""

from app.graphql.spec_sheets.strawberry.spec_sheet_input import (
    CreateSpecSheetInput,
    UpdateSpecSheetInput,
    MoveFolderInput,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_response import SpecSheetResponse
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_input import (
    HighlightRegionInput,
    CreateHighlightVersionInput,
    UpdateHighlightVersionInput,
    UpdateHighlightRegionsInput,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_response import (
    HighlightRegionResponse,
    HighlightVersionResponse,
)

__all__ = [
    # SpecSheet types
    "CreateSpecSheetInput",
    "UpdateSpecSheetInput",
    "MoveFolderInput",
    "SpecSheetResponse",
    # Highlight types
    "HighlightRegionInput",
    "CreateHighlightVersionInput",
    "UpdateHighlightVersionInput",
    "UpdateHighlightRegionsInput",
    "HighlightRegionResponse",
    "HighlightVersionResponse",
]
