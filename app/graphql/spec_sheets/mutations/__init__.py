"""SpecSheets mutations module."""

from app.graphql.spec_sheets.mutations.spec_sheets_mutations import SpecSheetsMutations
from app.graphql.spec_sheets.mutations.spec_sheet_highlights_mutations import (
    SpecSheetHighlightsMutations,
)

__all__ = ["SpecSheetsMutations", "SpecSheetHighlightsMutations"]
