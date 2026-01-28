from decimal import Decimal
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.errors.common_errors import ValidationError
from app.graphql.orders.strawberry.quote_detail_to_order_input import (
    QuoteDetailToOrderDetailInput,
)
from app.graphql.orders.validators.quote_factory_validator import (
    validate_quote_details_same_factory,
)


def _make_quote_detail(factory_id: UUID | None = None) -> MagicMock:
    detail = MagicMock()
    detail.id = uuid4()
    detail.factory_id = factory_id
    return detail


def _make_quote(details: list[MagicMock]) -> MagicMock:
    quote = MagicMock()
    quote.details = details
    return quote


def _make_input(quote_detail_id: UUID) -> QuoteDetailToOrderDetailInput:
    return QuoteDetailToOrderDetailInput(
        quantity=Decimal("1"),
        unit_price=Decimal("100"),
        quote_detail_id=quote_detail_id,
    )


class TestValidateQuoteDetailsSameFactory:
    def test_no_inputs_none_passes(self) -> None:
        quote = _make_quote([])
        validate_quote_details_same_factory(quote, None)

    def test_no_inputs_empty_list_passes(self) -> None:
        quote = _make_quote([])
        validate_quote_details_same_factory(quote, [])

    def test_single_factory_passes(self) -> None:
        factory_id = uuid4()
        detail1 = _make_quote_detail(factory_id=factory_id)
        detail2 = _make_quote_detail(factory_id=factory_id)
        quote = _make_quote([detail1, detail2])

        inputs = [_make_input(detail1.id), _make_input(detail2.id)]
        validate_quote_details_same_factory(quote, inputs)

    def test_all_null_factories_passes(self) -> None:
        detail1 = _make_quote_detail(factory_id=None)
        detail2 = _make_quote_detail(factory_id=None)
        quote = _make_quote([detail1, detail2])

        inputs = [_make_input(detail1.id), _make_input(detail2.id)]
        validate_quote_details_same_factory(quote, inputs)

    def test_mixed_null_and_single_factory_passes(self) -> None:
        factory_id = uuid4()
        detail1 = _make_quote_detail(factory_id=factory_id)
        detail2 = _make_quote_detail(factory_id=None)
        quote = _make_quote([detail1, detail2])

        inputs = [_make_input(detail1.id), _make_input(detail2.id)]
        validate_quote_details_same_factory(quote, inputs)

    def test_multiple_factories_raises(self) -> None:
        factory_id_1 = uuid4()
        factory_id_2 = uuid4()
        detail1 = _make_quote_detail(factory_id=factory_id_1)
        detail2 = _make_quote_detail(factory_id=factory_id_2)
        quote = _make_quote([detail1, detail2])

        inputs = [_make_input(detail1.id), _make_input(detail2.id)]

        with pytest.raises(ValidationError) as exc_info:
            validate_quote_details_same_factory(quote, inputs)

        assert "different manufacturers" in str(exc_info.value)

    def test_missing_quote_detail_ignored(self) -> None:
        factory_id = uuid4()
        detail1 = _make_quote_detail(factory_id=factory_id)
        quote = _make_quote([detail1])

        inputs = [_make_input(detail1.id), _make_input(uuid4())]
        validate_quote_details_same_factory(quote, inputs)

    def test_single_detail_passes(self) -> None:
        factory_id = uuid4()
        detail = _make_quote_detail(factory_id=factory_id)
        quote = _make_quote([detail])

        inputs = [_make_input(detail.id)]
        validate_quote_details_same_factory(quote, inputs)
