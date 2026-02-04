from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from commons.db.v6.commission.orders import OrderHeaderStatus, OrderStatus
from commons.db.v6.fulfillment import FulfillmentOrderStatus

from app.core.processors.context import EntityContext
from app.core.processors.events import RepositoryEvent
from app.graphql.v2.core.fulfillment.processors.update_order_on_fulfillment_processor import (
    UpdateOrderOnFulfillmentProcessor,
)


def _make_processor(
    session: AsyncMock | None = None,
) -> UpdateOrderOnFulfillmentProcessor:
    return UpdateOrderOnFulfillmentProcessor(session=session or AsyncMock())


class TestProcessStatusGuard:
    @pytest.mark.asyncio
    async def test_skips_non_shipped_status(self) -> None:
        session = AsyncMock()
        processor = _make_processor(session)

        fulfillment_order = MagicMock()
        fulfillment_order.status = FulfillmentOrderStatus.PICKING
        fulfillment_order.id = uuid4()

        context = EntityContext(
            entity=fulfillment_order,
            entity_id=fulfillment_order.id,
            event=RepositoryEvent.POST_UPDATE,
            original_entity=None,
        )

        await processor.process(context)
        session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_when_already_shipped(self) -> None:
        session = AsyncMock()
        processor = _make_processor(session)

        fulfillment_order = MagicMock()
        fulfillment_order.status = FulfillmentOrderStatus.SHIPPED
        fulfillment_order.id = uuid4()

        original = MagicMock()
        original.status = FulfillmentOrderStatus.SHIPPED

        context = EntityContext(
            entity=fulfillment_order,
            entity_id=fulfillment_order.id,
            event=RepositoryEvent.POST_UPDATE,
            original_entity=original,
        )

        await processor.process(context)
        session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_processes_when_transitioning_to_shipped(self) -> None:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        processor = _make_processor(session)

        fulfillment_order = MagicMock()
        fulfillment_order.status = FulfillmentOrderStatus.SHIPPED
        fulfillment_order.id = uuid4()
        fulfillment_order.order_id = uuid4()

        original = MagicMock()
        original.status = FulfillmentOrderStatus.SHIPPING

        context = EntityContext(
            entity=fulfillment_order,
            entity_id=fulfillment_order.id,
            event=RepositoryEvent.POST_UPDATE,
            original_entity=original,
        )

        await processor.process(context)
        session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_processes_when_no_original_entity(self) -> None:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        processor = _make_processor(session)

        fulfillment_order = MagicMock()
        fulfillment_order.status = FulfillmentOrderStatus.SHIPPED
        fulfillment_order.id = uuid4()
        fulfillment_order.order_id = uuid4()

        context = EntityContext(
            entity=fulfillment_order,
            entity_id=fulfillment_order.id,
            event=RepositoryEvent.POST_UPDATE,
            original_entity=None,
        )

        await processor.process(context)
        session.execute.assert_called_once()


class TestProcessEndToEnd:
    @pytest.mark.asyncio
    async def test_full_process_updates_order_and_details(self) -> None:
        session = AsyncMock()

        detail_id = uuid4()
        detail = MagicMock()
        detail.id = detail_id
        detail.shipping_balance = Decimal("10")
        detail.total = Decimal("10")
        detail.status = OrderStatus.OPEN

        order = MagicMock()
        order.id = uuid4()
        order.details = [detail]
        order.header_status = OrderHeaderStatus.OPEN

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = order
        session.execute.return_value = mock_result

        processor = _make_processor(session)

        line_item = MagicMock()
        line_item.order_detail_id = detail_id
        line_item.shipped_qty = Decimal("10")

        fulfillment_order = MagicMock()
        fulfillment_order.status = FulfillmentOrderStatus.SHIPPED
        fulfillment_order.id = uuid4()
        fulfillment_order.order_id = order.id
        fulfillment_order.line_items = [line_item]

        original = MagicMock()
        original.status = FulfillmentOrderStatus.SHIPPING

        context = EntityContext(
            entity=fulfillment_order,
            entity_id=fulfillment_order.id,
            event=RepositoryEvent.POST_UPDATE,
            original_entity=original,
        )

        await processor.process(context)

        assert detail.shipping_balance == Decimal("0")
        assert detail.status == OrderStatus.SHIPPED_COMPLETE
        assert order.status == OrderStatus.SHIPPED_COMPLETE
        assert order.header_status == OrderHeaderStatus.CLOSED
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_with_partial_shipment(self) -> None:
        session = AsyncMock()

        detail_id = uuid4()
        detail = MagicMock()
        detail.id = detail_id
        detail.shipping_balance = Decimal("10")
        detail.total = Decimal("10")
        detail.status = OrderStatus.OPEN

        order = MagicMock()
        order.id = uuid4()
        order.details = [detail]
        order.header_status = OrderHeaderStatus.OPEN

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = order
        session.execute.return_value = mock_result

        processor = _make_processor(session)

        line_item = MagicMock()
        line_item.order_detail_id = detail_id
        line_item.shipped_qty = Decimal("5")

        fulfillment_order = MagicMock()
        fulfillment_order.status = FulfillmentOrderStatus.SHIPPED
        fulfillment_order.id = uuid4()
        fulfillment_order.order_id = order.id
        fulfillment_order.line_items = [line_item]

        original = MagicMock()
        original.status = FulfillmentOrderStatus.SHIPPING

        context = EntityContext(
            entity=fulfillment_order,
            entity_id=fulfillment_order.id,
            event=RepositoryEvent.POST_UPDATE,
            original_entity=original,
        )

        await processor.process(context)

        assert detail.shipping_balance == Decimal("5")
        assert detail.status == OrderStatus.PARTIAL_SHIPPED
        assert order.status == OrderStatus.PARTIAL_SHIPPED
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_order_not_found(self) -> None:
        session = AsyncMock()

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        processor = _make_processor(session)

        fulfillment_order = MagicMock()
        fulfillment_order.status = FulfillmentOrderStatus.SHIPPED
        fulfillment_order.id = uuid4()
        fulfillment_order.order_id = uuid4()

        original = MagicMock()
        original.status = FulfillmentOrderStatus.SHIPPING

        context = EntityContext(
            entity=fulfillment_order,
            entity_id=fulfillment_order.id,
            event=RepositoryEvent.POST_UPDATE,
            original_entity=original,
        )

        await processor.process(context)
        session.flush.assert_not_called()
