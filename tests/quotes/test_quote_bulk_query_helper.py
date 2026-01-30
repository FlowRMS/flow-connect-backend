import pytest

from app.graphql.quotes.repositories.quote_bulk_query_helper import (
    build_find_quotes_by_quote_numbers_stmt,
)


class TestQuoteBulkQueryHelper:
    def test_build_find_quotes_by_quote_numbers_empty_returns_stmt(self) -> None:
        stmt = build_find_quotes_by_quote_numbers_stmt([])
        assert stmt is not None

    def test_build_find_quotes_by_quote_numbers_with_numbers_returns_stmt(
        self,
    ) -> None:
        stmt = build_find_quotes_by_quote_numbers_stmt(["Q-001", "Q-002"])
        assert stmt is not None
