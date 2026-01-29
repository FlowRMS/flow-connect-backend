from datetime import date
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from commons.db.v6.crm.quotes import Quote

from app.graphql.orders.factories.order_factory import OrderFactory


class TestOrderFactoryFromQuote:
    def test_from_quote_without_sold_to_customer_raises_error(self) -> None:
        """Test that creating an order from a quote without sold_to_customer_id fails."""
        mock_quote = MagicMock(spec=Quote)
        mock_quote.sold_to_customer_id = None
        mock_quote.inside_per_line_item = True
        mock_quote.outside_per_line_item = True
        mock_quote.end_user_per_line_item = False

        with pytest.raises(ValueError) as exc_info:
            OrderFactory.from_quote(
                quote=mock_quote,
                order_number="ORD-001",
                factory_id=uuid4(),
            )

        assert "Cannot create order from quote without sold_to_customer_id" in str(
            exc_info.value
        )

    def test_from_quote_with_sold_to_customer_succeeds(self) -> None:
        """Test that creating an order from a quote with sold_to_customer_id works."""
        sold_to_id = uuid4()
        factory_id = uuid4()

        mock_quote = MagicMock(spec=Quote)
        mock_quote.sold_to_customer_id = sold_to_id
        mock_quote.bill_to_customer_id = None
        mock_quote.inside_per_line_item = True
        mock_quote.outside_per_line_item = True
        mock_quote.end_user_per_line_item = False
        mock_quote.freight_terms = None
        mock_quote.details = []
        mock_quote.id = uuid4()
        mock_quote.job_id = None

        order = OrderFactory.from_quote(
            quote=mock_quote,
            order_number="ORD-002",
            factory_id=factory_id,
        )

        assert order.sold_to_customer_id == sold_to_id
        assert order.order_number == "ORD-002"
        assert order.factory_id == factory_id
