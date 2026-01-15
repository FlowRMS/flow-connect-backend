"""SpecSheets mutations module."""

from app.graphql.spec_sheets.mutations.folders_mutations import FoldersMutations
from app.graphql.spec_sheets.mutations.spec_sheet_highlights_mutations import (
    SpecSheetHighlightsMutations,
)
from app.graphql.spec_sheets.mutations.spec_sheets_mutations import SpecSheetsMutations

__all__ = ["FoldersMutations", "SpecSheetsMutations", "SpecSheetHighlightsMutations"]
