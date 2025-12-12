"""SpecSheets queries module."""

from app.graphql.spec_sheets.queries.spec_sheet_highlights_queries import (
    SpecSheetHighlightsQueries,
)
from app.graphql.spec_sheets.queries.spec_sheets_queries import SpecSheetsQueries

__all__ = ["SpecSheetsQueries", "SpecSheetHighlightsQueries"]
