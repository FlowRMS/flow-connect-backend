from datetime import date
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
import strawberry
from commons.db.v6.crm.quotes import PipelineStage, Quote, QuoteStatus

from app.graphql.quotes.strawberry.quote_input import QuoteInput
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


class TestQuoteNameField:
    def test_quote_input_with_name_creates_quote(self) -> None:
        """Test that a quote can be created with the new name field."""
        quote_input = QuoteInput(
            quote_number="Q-001",
            entity_date=date.today(),
            sold_to_customer_id=uuid4(),
            status=QuoteStatus.OPEN,
            pipeline_stage=PipelineStage.PROSPECT,
            details=[],
            name="Test Quote Name",
        )

        quote = quote_input.to_orm_model()

        assert quote.name == "Test Quote Name"
        assert quote.quote_number == "Q-001"

    def test_quote_input_without_name_creates_quote_with_none(self) -> None:
        """Test that a quote without name field has None."""
        quote_input = QuoteInput(
            quote_number="Q-002",
            entity_date=date.today(),
            sold_to_customer_id=uuid4(),
            status=QuoteStatus.OPEN,
            pipeline_stage=PipelineStage.PROSPECT,
            details=[],
        )

        quote = quote_input.to_orm_model()

        assert quote.name is None

    def test_quote_lite_response_includes_name(self) -> None:
        """Test that QuoteLiteResponse includes the name field."""
        mock_quote = MagicMock(spec=Quote)
        mock_quote.id = uuid4()
        mock_quote.created_at = MagicMock()
        mock_quote.created_by_id = uuid4()
        mock_quote.quote_number = "Q-003"
        mock_quote.name = "My Quote Name"
        mock_quote.entity_date = date.today()
        mock_quote.status = QuoteStatus.OPEN
        mock_quote.pipeline_stage = PipelineStage.PROSPECT
        mock_quote.published = True
        mock_quote.creation_type = MagicMock()
        mock_quote.sold_to_customer_id = uuid4()
        mock_quote.factory_per_line_item = False
        mock_quote.bill_to_customer_id = None
        mock_quote.payment_terms = None
        mock_quote.customer_ref = None
        mock_quote.freight_terms = None
        mock_quote.exp_date = None
        mock_quote.revise_date = None
        mock_quote.accept_date = None
        mock_quote.blanket = False
        mock_quote.duplicated_from = None
        mock_quote.version_of = None
        mock_quote.balance_id = uuid4()
        mock_quote.inside_per_line_item = True
        mock_quote.outside_per_line_item = True
        mock_quote.end_user_per_line_item = False

        response = QuoteLiteResponse.from_orm_model(mock_quote)

        assert response.name == "My Quote Name"


class TestQuoteNullableSoldToCustomer:
    def test_quote_input_without_sold_to_customer_creates_quote(self) -> None:
        """Test that a quote can be created with sold_to_customer_id = None."""
        quote_input = QuoteInput(
            quote_number="Q-004",
            entity_date=date.today(),
            sold_to_customer_id=None,
            status=QuoteStatus.OPEN,
            pipeline_stage=PipelineStage.PROSPECT,
            details=[],
        )

        quote = quote_input.to_orm_model()

        assert quote.sold_to_customer_id is None
        assert quote.quote_number == "Q-004"

    def test_quote_response_sold_to_customer_returns_none_when_null(self) -> None:
        """Test that QuoteResponse.sold_to_customer returns None when null."""
        mock_quote = MagicMock(spec=Quote)
        mock_quote.id = uuid4()
        mock_quote.created_at = MagicMock()
        mock_quote.created_by_id = uuid4()
        mock_quote.quote_number = "Q-005"
        mock_quote.name = None
        mock_quote.entity_date = date.today()
        mock_quote.status = QuoteStatus.OPEN
        mock_quote.pipeline_stage = PipelineStage.PROSPECT
        mock_quote.published = True
        mock_quote.creation_type = MagicMock()
        mock_quote.sold_to_customer_id = None
        mock_quote.sold_to_customer = None
        mock_quote.factory_per_line_item = False
        mock_quote.bill_to_customer_id = None
        mock_quote.bill_to_customer = None
        mock_quote.payment_terms = None
        mock_quote.customer_ref = None
        mock_quote.freight_terms = None
        mock_quote.exp_date = None
        mock_quote.revise_date = None
        mock_quote.accept_date = None
        mock_quote.blanket = False
        mock_quote.duplicated_from = None
        mock_quote.version_of = None
        mock_quote.balance_id = uuid4()
        mock_quote.inside_per_line_item = True
        mock_quote.outside_per_line_item = True
        mock_quote.end_user_per_line_item = False
        mock_quote.created_by = MagicMock()
        mock_quote.balance = MagicMock()
        mock_quote.details = []
        mock_quote.job = None

        response = QuoteResponse.from_orm_model(mock_quote)

        assert response.sold_to_customer_id is None
        assert response.sold_to_customer() is None
