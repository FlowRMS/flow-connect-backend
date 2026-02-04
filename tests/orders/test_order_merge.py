from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_detail_input import OrderDetailInput
from app.graphql.orders.strawberry.order_input import OrderInput


class TestOrderMergeFromInput:
    def test_merge_order_from_input_updates_existing_details_by_item_number(
        self,
    ) -> None:
        order_id = uuid4()
        customer_id = uuid4()
        factory_id = uuid4()
        end_user_id = uuid4()

        existing_detail_1 = MagicMock()
        existing_detail_1.item_number = 1
        existing_detail_1.id = uuid4()
        existing_detail_1.order_id = order_id

        existing_detail_2 = MagicMock()
        existing_detail_2.item_number = 2
        existing_detail_2.id = uuid4()
        existing_detail_2.order_id = order_id

        existing_order = MagicMock()
        existing_order.id = order_id
        existing_order.details = [existing_detail_1, existing_detail_2]

        new_detail_1 = OrderDetailInput(
            item_number=1,
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            end_user_id=end_user_id,
        )
        new_detail_2 = OrderDetailInput(
            item_number=2,
            quantity=Decimal("5"),
            unit_price=Decimal("50"),
            end_user_id=end_user_id,
        )
        new_detail_3 = OrderDetailInput(
            item_number=3,
            quantity=Decimal("1"),
            unit_price=Decimal("200"),
            end_user_id=end_user_id,
        )

        order_input = OrderInput(
            order_number="ORD-001",
            entity_date=date.today(),
            due_date=date.today(),
            sold_to_customer_id=customer_id,
            factory_id=factory_id,
            details=[new_detail_1, new_detail_2, new_detail_3],
        )

        repo = MagicMock()
        service = OrderService(
            repository=repo,
            quotes_repository=MagicMock(),
            auth_info=MagicMock(),
        )

        merged = service._merge_order_from_input(existing_order, order_input)

        assert merged is existing_order
        assert len(merged.details) == 3
        detail_by_item = {d.item_number: d for d in merged.details}
        assert 1 in detail_by_item
        assert 2 in detail_by_item
        assert 3 in detail_by_item
        assert detail_by_item[1].id == existing_detail_1.id
        assert detail_by_item[2].id == existing_detail_2.id
        assert detail_by_item[1].quantity == Decimal("10")
        assert detail_by_item[3].quantity == Decimal("1")
