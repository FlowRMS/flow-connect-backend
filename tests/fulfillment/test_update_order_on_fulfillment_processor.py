from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from commons.db.v6.commission.orders import OrderHeaderStatus, OrderStatus

from app.core.processors.events import RepositoryEvent
from app.graphql.v2.core.fulfillment.processors.update_order_on_fulfillment_processor import (
    UpdateOrderOnFulfillmentProcessor,
)


def _make_processor(session: AsyncMock | None = None) -> UpdateOrderOnFulfillmentProcessor:
    return UpdateOrderOnFulfillmentProcessor(session=session or AsyncMock())


class TestProcessorEvents:
    def test_events_returns_post_update(self) -> None:
        processor = _make_processor()
        assert processor.events == [RepositoryEvent.POST_UPDATE]


class TestCalculateDetailStatus:
    def test_over_shipped(self) -> None:
        processor = _make_processor()
        result = processor._calculate_detail_status(Decimal("-1"), Decimal("10"))
        assert result == OrderStatus.OVER_SHIPPED

    def test_shipped_complete_zero_balance(self) -> None:
        processor = _make_processor()
        result = processor._calculate_detail_status(Decimal("0"), Decimal("10"))
        assert result == OrderStatus.SHIPPED_COMPLETE

    def test_shipped_complete_near_zero(self) -> None:
        processor = _make_processor()
        result = processor._calculate_detail_status(Decimal("0.001"), Decimal("10"))
        assert result == OrderStatus.SHIPPED_COMPLETE

    def test_open_balance_equals_total(self) -> None:
        processor = _make_processor()
        result = processor._calculate_detail_status(Decimal("10"), Decimal("10"))
        assert result == OrderStatus.OPEN

    def test_partial_shipped(self) -> None:
        processor = _make_processor()
        result = processor._calculate_detail_status(Decimal("5"), Decimal("10"))
        assert result == OrderStatus.PARTIAL_SHIPPED

    def test_over_shipped_large_negative(self) -> None:
        processor = _make_processor()
        result = processor._calculate_detail_status(Decimal("-100"), Decimal("50"))
        assert result == OrderStatus.OVER_SHIPPED


class TestUpdateOrderStatus:
    def test_all_open(self) -> None:
        processor = _make_processor()
        order = MagicMock()
        d1 = MagicMock()
        d1.status = OrderStatus.OPEN
        d2 = MagicMock()
        d2.status = OrderStatus.OPEN
        order.details = [d1, d2]

        processor._update_order_status(order)
        assert order.status == OrderStatus.OPEN

    def test_all_shipped_complete_closes_header(self) -> None:
        processor = _make_processor()
        order = MagicMock()
        d1 = MagicMock()
        d1.status = OrderStatus.SHIPPED_COMPLETE
        d2 = MagicMock()
        d2.status = OrderStatus.SHIPPED_COMPLETE
        order.details = [d1, d2]
        order.header_status = OrderHeaderStatus.OPEN

        processor._update_order_status(order)
        assert order.status == OrderStatus.SHIPPED_COMPLETE
        assert order.header_status == OrderHeaderStatus.CLOSED

    def test_shipped_complete_does_not_overwrite_cancelled_header(self) -> None:
        processor = _make_processor()
        order = MagicMock()
        d1 = MagicMock()
        d1.status = OrderStatus.SHIPPED_COMPLETE
        order.details = [d1]
        order.header_status = OrderHeaderStatus.CANCELLED

        processor._update_order_status(order)
        assert order.status == OrderStatus.SHIPPED_COMPLETE
        assert order.header_status == OrderHeaderStatus.CANCELLED

    def test_shipped_complete_does_not_overwrite_closed_header(self) -> None:
        processor = _make_processor()
        order = MagicMock()
        d1 = MagicMock()
        d1.status = OrderStatus.SHIPPED_COMPLETE
        order.details = [d1]
        order.header_status = OrderHeaderStatus.CLOSED

        processor._update_order_status(order)
        assert order.status == OrderStatus.SHIPPED_COMPLETE
        assert order.header_status == OrderHeaderStatus.CLOSED

    def test_any_over_shipped(self) -> None:
        processor = _make_processor()
        order = MagicMock()
        d1 = MagicMock()
        d1.status = OrderStatus.OVER_SHIPPED
        d2 = MagicMock()
        d2.status = OrderStatus.OPEN
        order.details = [d1, d2]

        processor._update_order_status(order)
        assert order.status == OrderStatus.OVER_SHIPPED

    def test_mixed_statuses_partial_shipped(self) -> None:
        processor = _make_processor()
        order = MagicMock()
        d1 = MagicMock()
        d1.status = OrderStatus.SHIPPED_COMPLETE
        d2 = MagicMock()
        d2.status = OrderStatus.OPEN
        order.details = [d1, d2]

        processor._update_order_status(order)
        assert order.status == OrderStatus.PARTIAL_SHIPPED

    def test_no_details_does_nothing(self) -> None:
        processor = _make_processor()
        order = MagicMock()
        order.details = []
        original_status = order.status

        processor._update_order_status(order)
        assert order.status == original_status
