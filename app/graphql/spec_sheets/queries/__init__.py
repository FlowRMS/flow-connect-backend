"""SpecSheets queries module."""

from app.graphql.spec_sheets.queries.spec_sheets_queries import SpecSheetsQueries
from app.graphql.spec_sheets.queries.spec_sheet_highlights_queries import (
    SpecSheetHighlightsQueries,
)

__all__ = ["SpecSheetsQueries", "SpecSheetHighlightsQueries"]
