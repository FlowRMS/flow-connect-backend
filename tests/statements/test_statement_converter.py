from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.workers.document_execution.converters.entity_mapping import EntityMapping
from app.workers.document_execution.converters.statement_converter import (
    DEFAULT_QUANTITY,
    StatementConverter,
)


def _make_mock_detail_dto(
    *,
    flow_detail_index: int = 0,
    quantity_determined: Decimal | None = None,
    unit_price_determined: Decimal | None = None,
    commission_rate_determined: Decimal | None = None,
    commission_discount_rate: Decimal | None = None,
    discount_rate: Decimal | None = None,
    total_line_commission: Decimal | None = None,
    paid_commission_amount: Decimal | None = None,
    factory_part_number: str | None = None,
    customer_part_number: str | None = None,
    description: str | None = None,
    lead_time: str | None = None,
) -> MagicMock:
    """Create a mock CommissionStatementDetailDTO with the specified fields."""
    dto = MagicMock()
    dto.flow_detail_index = flow_detail_index
    dto.quantity_determined = quantity_determined
    dto.unit_price_determined = unit_price_determined
    dto.commission_rate_determined = commission_rate_determined
    dto.commission_discount_rate = commission_discount_rate
    dto.discount_rate = discount_rate
    dto.total_line_commission = total_line_commission
    dto.paid_commission_amount = paid_commission_amount
    dto.factory_part_number = factory_part_number
    dto.customer_part_number = customer_part_number
    dto.description = description
    dto.lead_time = lead_time
    return dto


def _make_converter() -> StatementConverter:
    """Create a StatementConverter with mocked dependencies."""
    session = AsyncMock()
    dto_loader_service = MagicMock()
    statement_service = MagicMock()
    orders_repository = MagicMock()
    order_detail_matcher = MagicMock()

    # Mock async methods on orders_repository
    orders_repository.find_order_by_id = AsyncMock(return_value=None)

    converter = StatementConverter(
        session=session,
        dto_loader_service=dto_loader_service,
        statement_service=statement_service,
        orders_repository=orders_repository,
        order_detail_matcher=order_detail_matcher,
    )
    # Mock order matching to return None (no matching)
    converter.order_detail_matcher.match_order_detail = AsyncMock(return_value=None)
    return converter


def _make_entity_mapping(
    *,
    factory_id: None = None,
    sold_to_customer_id: None = None,
    products: dict[int, ...] | None = None,
    end_users: dict[int, ...] | None = None,
    orders: dict[int, ...] | None = None,
    invoices: dict[int, ...] | None = None,
) -> EntityMapping:
    """Create an EntityMapping with the specified fields."""
    return EntityMapping(
        factory_id=factory_id or uuid4(),
        sold_to_customer_id=sold_to_customer_id or uuid4(),
        products=products or {},
        end_users=end_users or {},
        orders=orders or {},
        invoices=invoices or {},
    )


class TestStatementConverterConvertDetailCommission:
    """Tests for StatementConverter._convert_detail() commission sourcing logic."""

    @pytest.mark.asyncio
    async def test_commission_from_total_line_commission_when_provided(self) -> None:
        """Commission should come from total_line_commission when available."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            total_line_commission=Decimal("50"),
            paid_commission_amount=Decimal("30"),  # Should be ignored
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        # total_line_commission takes priority over paid_commission_amount
        assert result.commission == Decimal("50")

    @pytest.mark.asyncio
    async def test_commission_fallback_to_paid_commission_amount(self) -> None:
        """Commission should fall back to paid_commission_amount when total_line_commission is None."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            total_line_commission=None,
            paid_commission_amount=Decimal("45"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        # Should fall back to paid_commission_amount
        assert result.commission == Decimal("45")

    @pytest.mark.asyncio
    async def test_commission_none_when_both_sources_none(self) -> None:
        """Commission should be None when both total_line_commission and paid_commission_amount are None."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            total_line_commission=None,
            paid_commission_amount=None,
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        # Commission should be None, meaning rate-based calculation will be used in to_orm_model
        assert result.commission is None

    @pytest.mark.asyncio
    async def test_zero_total_line_commission_is_used(self) -> None:
        """Zero total_line_commission should be respected as a valid value."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            total_line_commission=Decimal("0"),  # Explicitly zero
            paid_commission_amount=Decimal("50"),  # Should be ignored
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        # Zero should be used as a valid value
        assert result.commission == Decimal("0")


class TestStatementConverterConvertDetailQuantity:
    """Tests for StatementConverter._convert_detail() quantity fallback behavior."""

    @pytest.mark.asyncio
    async def test_quantity_from_dto_when_provided(self) -> None:
        """Quantity should come from DTO when quantity_determined is provided."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("25"),
            unit_price_determined=Decimal("100"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.quantity == Decimal("25")

    @pytest.mark.asyncio
    async def test_quantity_fallback_to_default_when_none(self) -> None:
        """Quantity should fall back to DEFAULT_QUANTITY when quantity_determined is None."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=None,
            unit_price_determined=Decimal("100"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.quantity == DEFAULT_QUANTITY
        assert result.quantity == Decimal("1")

    @pytest.mark.asyncio
    async def test_quantity_decimal_from_various_types(self) -> None:
        """Quantity should be properly converted to Decimal from the DTO value."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        # Test with float-like value
        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=10.5,  # May come as float from JSON
            unit_price_determined=Decimal("100"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.quantity == Decimal("10.5")


class TestStatementConverterConvertDetailRates:
    """Tests for StatementConverter._convert_detail() rate derivation logic."""

    @pytest.mark.asyncio
    async def test_commission_rate_from_dto_when_provided(self) -> None:
        """Commission rate should come from DTO when commission_rate_determined is provided."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            commission_rate_determined=Decimal("8"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),  # Should be ignored
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.commission_rate == Decimal("8")

    @pytest.mark.asyncio
    async def test_commission_rate_fallback_to_factory_default(self) -> None:
        """Commission rate should fall back to factory default when not in DTO."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            commission_rate_determined=None,
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("12"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.commission_rate == Decimal("12")

    @pytest.mark.asyncio
    async def test_commission_discount_rate_from_dto_when_provided(self) -> None:
        """Commission discount rate should come from DTO when provided."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            commission_discount_rate=Decimal("3"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("10"),  # Should be ignored
            default_discount_rate=Decimal("0"),
        )

        assert result.commission_discount_rate == Decimal("3")

    @pytest.mark.asyncio
    async def test_commission_discount_rate_fallback_to_factory_default(self) -> None:
        """Commission discount rate should fall back to factory default when not in DTO."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            commission_discount_rate=None,
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("7"),
            default_discount_rate=Decimal("0"),
        )

        assert result.commission_discount_rate == Decimal("7")

    @pytest.mark.asyncio
    async def test_discount_rate_from_dto_when_provided(self) -> None:
        """Discount rate should come from DTO when provided."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            discount_rate=Decimal("15"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("20"),  # Should be ignored
        )

        assert result.discount_rate == Decimal("15")

    @pytest.mark.asyncio
    async def test_discount_rate_fallback_to_factory_default(self) -> None:
        """Discount rate should fall back to factory default when not in DTO."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            discount_rate=None,
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("25"),
        )

        assert result.discount_rate == Decimal("25")


class TestStatementConverterConvertDetailUnitPrice:
    """Tests for StatementConverter._convert_detail() unit price handling."""

    @pytest.mark.asyncio
    async def test_unit_price_from_dto_when_provided(self) -> None:
        """Unit price should come from DTO when unit_price_determined is provided."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("199.99"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.unit_price == Decimal("199.99")

    @pytest.mark.asyncio
    async def test_unit_price_fallback_to_zero_when_none(self) -> None:
        """Unit price should fall back to 0 when unit_price_determined is None."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping()

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=None,
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.unit_price == Decimal("0")


class TestStatementConverterConvertDetailProductAdhoc:
    """Tests for StatementConverter._convert_detail() adhoc product name logic."""

    @pytest.mark.asyncio
    async def test_adhoc_name_from_factory_part_number(self) -> None:
        """Adhoc product name should use factory_part_number when available and no product_id."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping(products={})

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            factory_part_number="FPN-123",
            customer_part_number="CPN-456",
            description="Some description",
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        # factory_part_number takes priority
        assert result.product_name_adhoc == "FPN-123"

    @pytest.mark.asyncio
    async def test_adhoc_name_fallback_to_customer_part_number(self) -> None:
        """Adhoc product name should fall back to customer_part_number when no factory_part_number."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping(products={})

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            factory_part_number=None,
            customer_part_number="CPN-789",
            description="Some description",
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.product_name_adhoc == "CPN-789"

    @pytest.mark.asyncio
    async def test_adhoc_name_fallback_to_description_truncated(self) -> None:
        """Adhoc product name should fall back to description (truncated to 100 chars)."""
        converter = _make_converter()
        entity_mapping = _make_entity_mapping(products={})

        long_description = "A" * 150  # 150 characters

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            factory_part_number=None,
            customer_part_number=None,
            description=long_description,
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        # Description should be truncated to 100 characters
        assert result.product_name_adhoc == "A" * 100

    @pytest.mark.asyncio
    async def test_no_adhoc_name_when_product_id_exists(self) -> None:
        """Adhoc product name should be None when product_id is mapped."""
        converter = _make_converter()
        product_id = uuid4()
        entity_mapping = _make_entity_mapping(products={0: product_id})

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
            factory_part_number="FPN-123",
            customer_part_number="CPN-456",
            description="Some description",
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        # product_id is set, so adhoc fields should be None
        assert result.product_id == product_id
        assert result.product_name_adhoc is None
        assert result.product_description_adhoc is None


class TestStatementConverterConvertDetailEntityMapping:
    """Tests for StatementConverter._convert_detail() entity ID mapping."""

    @pytest.mark.asyncio
    async def test_maps_product_id_from_entity_mapping(self) -> None:
        """Product ID should be retrieved from entity mapping based on flow_detail_index."""
        converter = _make_converter()
        product_id = uuid4()
        entity_mapping = _make_entity_mapping(products={0: product_id})

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.product_id == product_id

    @pytest.mark.asyncio
    async def test_maps_order_id_from_entity_mapping(self) -> None:
        """Order ID should be retrieved from entity mapping based on flow_detail_index."""
        converter = _make_converter()
        order_id = uuid4()
        entity_mapping = _make_entity_mapping(orders={0: order_id})

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.order_id == order_id

    @pytest.mark.asyncio
    async def test_maps_invoice_id_from_entity_mapping(self) -> None:
        """Invoice ID should be retrieved from entity mapping based on flow_detail_index."""
        converter = _make_converter()
        invoice_id = uuid4()
        entity_mapping = _make_entity_mapping(invoices={0: invoice_id})

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.invoice_id == invoice_id

    @pytest.mark.asyncio
    async def test_maps_end_user_id_from_entity_mapping(self) -> None:
        """End user ID should be retrieved from entity mapping based on flow_detail_index."""
        converter = _make_converter()
        end_user_id = uuid4()
        entity_mapping = _make_entity_mapping(end_users={0: end_user_id})

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.end_user_id == end_user_id

    @pytest.mark.asyncio
    async def test_sold_to_customer_id_from_entity_mapping(self) -> None:
        """Sold to customer ID should come from entity mapping."""
        converter = _make_converter()
        sold_to_id = uuid4()
        entity_mapping = _make_entity_mapping(sold_to_customer_id=sold_to_id)

        dto = _make_mock_detail_dto(
            flow_detail_index=0,
            quantity_determined=Decimal("10"),
            unit_price_determined=Decimal("100"),
        )

        result = await converter._convert_detail(
            detail=dto,
            item_number=1,
            entity_mapping=entity_mapping,
            default_commission_rate=Decimal("5"),
            default_commission_discount=Decimal("0"),
            default_discount_rate=Decimal("0"),
        )

        assert result.sold_to_customer_id == sold_to_id
