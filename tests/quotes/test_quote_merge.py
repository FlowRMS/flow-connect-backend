from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

from commons.db.v6.crm.quotes import PipelineStage, QuoteStatus

from app.graphql.quotes.services.quote_service import QuoteService
from app.graphql.quotes.strawberry.quote_detail_input import QuoteDetailInput
from app.graphql.quotes.strawberry.quote_input import QuoteInput


class TestQuoteMergeFromInput:
    def test_merge_quote_from_input_updates_existing_details_by_item_number(
        self,
    ) -> None:
        quote_id = uuid4()
        factory_id = uuid4()
        end_user_id = uuid4()

        existing_detail_1 = MagicMock()
        existing_detail_1.item_number = 1
        existing_detail_1.id = uuid4()
        existing_detail_1.quote_id = quote_id

        existing_quote = MagicMock()
        existing_quote.id = quote_id
        existing_quote.details = [existing_detail_1]

        new_detail_1 = QuoteDetailInput(
            item_number=1,
            quantity=Decimal("20"),
            unit_price=Decimal("150"),
            end_user_id=end_user_id,
            factory_id=factory_id,
        )
        new_detail_2 = QuoteDetailInput(
            item_number=2,
            quantity=Decimal("3"),
            unit_price=Decimal("75"),
            end_user_id=end_user_id,
            factory_id=factory_id,
        )

        quote_input = QuoteInput(
            quote_number="Q-001",
            entity_date=date.today(),
            sold_to_customer_id=uuid4(),
            status=QuoteStatus.OPEN,
            pipeline_stage=PipelineStage.PROPOSAL,
            details=[new_detail_1, new_detail_2],
        )

        repo = MagicMock()
        service = QuoteService(
            repository=repo,
            pre_opportunity_repository=MagicMock(),
            auth_info=MagicMock(),
        )

        merged = service._merge_quote_from_input(existing_quote, quote_input)

        assert merged is existing_quote
        assert len(merged.details) == 2
        detail_by_item = {d.item_number: d for d in merged.details}
        assert 1 in detail_by_item
        assert 2 in detail_by_item
        assert detail_by_item[1].id == existing_detail_1.id
        assert detail_by_item[1].quantity == Decimal("20")
        assert detail_by_item[2].quantity == Decimal("3")
