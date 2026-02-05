from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from commons.db.v6 import AutoNumberEntityType

from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_detail_input import OrderDetailInput
from app.graphql.orders.strawberry.order_input import OrderInput


@pytest.fixture
def mock_repository() -> AsyncMock:
    repo = AsyncMock()
    repo.order_number_exists.return_value = False
    repo.create_with_balance.return_value = MagicMock(id=uuid4())
    return repo


@pytest.fixture
def mock_quotes_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_auto_number_service() -> MagicMock:
    service = MagicMock()
    service.needs_generation = MagicMock(side_effect=lambda x: not x or not x.strip())
    service.generate_number = AsyncMock(return_value="Flow-1")
    return service


@pytest.fixture
def mock_auth_info() -> MagicMock:
    return MagicMock()


@pytest.fixture
def order_service(
    mock_repository: AsyncMock,
    mock_quotes_repository: AsyncMock,
    mock_auto_number_service: MagicMock,
    mock_auth_info: MagicMock,
) -> OrderService:
    return OrderService(
        repository=mock_repository,
        quotes_repository=mock_quotes_repository,
        auto_number_settings_service=mock_auto_number_service,
        auth_info=mock_auth_info,
    )


def make_order_input(order_number: str | None) -> OrderInput:
    return OrderInput(
        order_number=order_number or "",
        entity_date=date.today(),
        due_date=date.today(),
        sold_to_customer_id=uuid4(),
        factory_id=uuid4(),
        details=[
            OrderDetailInput(
                item_number=1,
                quantity=Decimal("10"),
                unit_price=Decimal("100"),
                end_user_id=uuid4(),
            )
        ],
    )


class TestOrderServiceAutoNumber:
    @pytest.mark.asyncio
    async def test_create_order_with_empty_number_generates_auto_number(
        self,
        order_service: OrderService,
        mock_auto_number_service: MagicMock,
    ) -> None:
        order_input = make_order_input("")

        _ = await order_service.create_order(order_input)

        mock_auto_number_service.needs_generation.assert_called_once_with("")
        mock_auto_number_service.generate_number.assert_awaited_once_with(
            AutoNumberEntityType.ORDER
        )
        assert order_input.order_number == "Flow-1"

    @pytest.mark.asyncio
    async def test_create_order_with_provided_number_uses_provided(
        self,
        order_service: OrderService,
        mock_auto_number_service: MagicMock,
    ) -> None:
        order_input = make_order_input("CUSTOM-123")

        _ = await order_service.create_order(order_input)

        mock_auto_number_service.needs_generation.assert_called_once_with("CUSTOM-123")
        mock_auto_number_service.generate_number.assert_not_awaited()
        assert order_input.order_number == "CUSTOM-123"

    @pytest.mark.asyncio
    async def test_create_order_with_whitespace_generates_auto_number(
        self,
        order_service: OrderService,
        mock_auto_number_service: MagicMock,
    ) -> None:
        order_input = make_order_input("   ")

        _ = await order_service.create_order(order_input)

        mock_auto_number_service.generate_number.assert_awaited_once_with(
            AutoNumberEntityType.ORDER
        )
        assert order_input.order_number == "Flow-1"
