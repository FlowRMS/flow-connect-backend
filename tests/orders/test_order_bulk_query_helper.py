from uuid import uuid4

from app.graphql.orders.repositories.order_bulk_query_helper import (
    build_find_orders_by_number_customer_pairs_stmt,
)


class TestOrderBulkQueryHelper:
    def test_build_find_orders_by_number_customer_pairs_empty_returns_stmt(
        self,
    ) -> None:
        stmt = build_find_orders_by_number_customer_pairs_stmt([])
        assert stmt is not None

    def test_build_find_orders_by_number_customer_pairs_with_pairs_returns_stmt(
        self,
    ) -> None:
        pairs = [("ORD-001", uuid4()), ("ORD-002", uuid4())]
        stmt = build_find_orders_by_number_customer_pairs_stmt(pairs)
        assert stmt is not None
