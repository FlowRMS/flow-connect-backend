"""GraphQL Strawberry types for SpecSheets."""

from app.graphql.spec_sheets.strawberry.folder_input import (
    CreateFolderInput,
    DeleteFolderInput,
    RenameFolderInput,
)
from app.graphql.spec_sheets.strawberry.folder_response import (
    RenameSpecSheetFolderResult,
    SpecSheetFolderResponse,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_input import (
    CreateHighlightVersionInput,
    HighlightRegionInput,
    UpdateHighlightRegionsInput,
    UpdateHighlightVersionInput,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_response import (
    HighlightRegionResponse,
    HighlightVersionResponse,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_input import (
    CreateSpecSheetInput,
    MoveFolderInput,
    UpdateSpecSheetInput,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_response import SpecSheetResponse

__all__ = [
    # Folder types
    "CreateFolderInput",
    "RenameFolderInput",
    "DeleteFolderInput",
    "SpecSheetFolderResponse",
    "RenameSpecSheetFolderResult",
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
