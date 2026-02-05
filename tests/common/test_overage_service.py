#!/usr/bin/env python3
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# Check if required modules are available
try:
    from commons.db.v6.core.factories import Factory, OverageTypeEnum
    from commons.db.v6.core.products import Product, ProductCpn, ProductQuantityPricing

    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not MODULES_AVAILABLE,
    reason="Required modules not available. Update pyproject.toml to use local flowbot-commons.",
)


# ============================================================================
# Test Factory Overage Fields
# ============================================================================


class TestFactoryOverageFields:
    """Test that Factory model has overage-related fields."""

    def test_factory_has_overage_allowed_field(self):
        """Verify Factory has overage_allowed field."""
        assert hasattr(Factory, "overage_allowed")

    def test_factory_has_overage_type_field(self):
        """Verify Factory has overage_type field."""
        assert hasattr(Factory, "overage_type")

    def test_factory_has_rep_overage_share_field(self):
        """Verify Factory has rep_overage_share field."""
        assert hasattr(Factory, "rep_overage_share")

    def test_overage_type_enum_values(self):
        """Verify OverageTypeEnum has correct values."""
        assert OverageTypeEnum.BY_LINE.value == 0
        assert OverageTypeEnum.BY_TOTAL.value == 1


# ============================================================================
# Test Product Pricing Models
# ============================================================================


class TestProductPricingModels:
    """Test that product pricing models have required fields."""

    def test_product_cpn_has_required_fields(self):
        """Verify ProductCpn has fields for customer-specific pricing."""
        required_fields = [
            "product_id",
            "customer_id",
            "unit_price",
            "commission_rate",
        ]
        for field in required_fields:
            assert hasattr(ProductCpn, field), f"ProductCpn missing field: {field}"

    def test_product_quantity_pricing_has_required_fields(self):
        """Verify ProductQuantityPricing has fields for quantity-based pricing."""
        required_fields = [
            "product_id",
            "quantity_low",
            "quantity_high",
            "unit_price",
        ]
        for field in required_fields:
            assert hasattr(ProductQuantityPricing, field), (
                f"ProductQuantityPricing missing field: {field}"
            )


# ============================================================================
# Test OverageService
# ============================================================================


class TestOverageService:
    """Test OverageService calculation logic."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock AsyncSession."""
        session = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def mock_product(self):
        """Create a mock Product."""
        product = MagicMock()
        product.id = uuid4()
        product.unit_price = Decimal("100.00")
        product.default_commission_rate = Decimal("10.00")
        return product

    @pytest.fixture
    def mock_factory(self):
        """Create a mock Factory with overage enabled."""
        factory = MagicMock()
        factory.id = uuid4()
        factory.overage_allowed = True
        factory.overage_type = OverageTypeEnum.BY_LINE
        factory.rep_overage_share = Decimal("100.00")
        factory.base_commission_rate = Decimal("8.00")
        return factory

    def test_overage_service_can_be_imported(self):
        """Verify OverageService can be imported."""
        from app.graphql.common.services.overage_service import OverageService

        assert OverageService is not None

    def test_overage_record_has_required_fields(self):
        """Verify OverageRecord has all expected fields."""
        from app.graphql.common.strawberry.overage_record import OverageRecord

        record = OverageRecord()
        assert hasattr(record, "effective_commission_rate")
        assert hasattr(record, "overage_unit_price")
        assert hasattr(record, "base_unit_price")
        assert hasattr(record, "rep_share")
        assert hasattr(record, "level_rate")
        assert hasattr(record, "level_unit_price")
        assert hasattr(record, "overage_type")
        assert hasattr(record, "error_message")
        assert hasattr(record, "success")

    def test_overage_record_defaults(self):
        """Verify OverageRecord has correct defaults."""
        from app.graphql.common.strawberry.overage_record import OverageRecord

        record = OverageRecord()
        assert record.success is True
        assert record.error_message is None

    def test_overage_type_enum_conversion(self):
        """Verify DB enum converts to GraphQL enum correctly."""
        from app.graphql.common.services.overage_service import _convert_overage_type
        from app.graphql.common.strawberry.overage_record import (
            OverageTypeEnum as GqlEnum,
        )

        result_by_line = _convert_overage_type(OverageTypeEnum.BY_LINE)
        assert result_by_line == GqlEnum.BY_LINE

        result_by_total = _convert_overage_type(OverageTypeEnum.BY_TOTAL)
        assert result_by_total == GqlEnum.BY_TOTAL


# ============================================================================
# Test Commission Rate Priority
# ============================================================================


class TestCommissionRatePriority:
    """Test commission rate selection priority."""

    def test_get_product_commission_rate_priority(self):
        """
        Verify commission rate priority:
        1. Customer-specific rate (from ProductCpn)
        2. Product default_commission_rate
        3. Factory base_commission_rate
        """
        from app.graphql.common.services.overage_service import OverageService

        # Create mock session
        session = AsyncMock()
        service = OverageService(session)

        # Create mock product and factory
        product = MagicMock()
        product.default_commission_rate = Decimal("10.00")

        factory = MagicMock()
        factory.base_commission_rate = Decimal("8.00")

        # Test priority 1: Customer rate wins
        result = service._get_product_commission_rate(
            product, factory, customer_rate_override=12.5
        )
        assert result == 12.5

        # Test priority 2: Product rate when no customer rate
        result = service._get_product_commission_rate(
            product, factory, customer_rate_override=None
        )
        assert result == 10.0

        # Test priority 3: Factory rate when no product rate
        product.default_commission_rate = None
        result = service._get_product_commission_rate(
            product, factory, customer_rate_override=None
        )
        assert result == 8.0

        # Test None when no rates available
        factory.base_commission_rate = None
        result = service._get_product_commission_rate(
            product, factory, customer_rate_override=None
        )
        assert result is None


# ============================================================================
# Test Division by Zero Protection
# ============================================================================


class TestDivisionByZeroProtection:
    """Test that division by zero is properly handled."""

    @pytest.mark.asyncio
    async def test_zero_unit_price_raises_error(self):
        """Verify ValueError is raised when detail_unit_price is 0."""
        from app.graphql.common.services.overage_service import OverageService

        session = AsyncMock()
        service = OverageService(session)

        with pytest.raises(ValueError) as exc_info:
            await service.find_effective_commission_rate_and_overage(
                product_id=uuid4(),
                detail_unit_price=0,  # This should raise
                factory_id=uuid4(),
                end_user_id=uuid4(),
                quantity=1.0,
            )

        assert "must be positive" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_negative_unit_price_raises_error(self):
        """Verify ValueError is raised when detail_unit_price is negative."""
        from app.graphql.common.services.overage_service import OverageService

        session = AsyncMock()
        service = OverageService(session)

        with pytest.raises(ValueError) as exc_info:
            await service.find_effective_commission_rate_and_overage(
                product_id=uuid4(),
                detail_unit_price=-10.0,  # This should raise
                factory_id=uuid4(),
                end_user_id=uuid4(),
                quantity=1.0,
            )

        assert "must be positive" in str(exc_info.value)


# ============================================================================
# Test Error Feedback
# ============================================================================


class TestErrorFeedback:
    """Test that errors are properly communicated via OverageRecord."""

    @pytest.mark.asyncio
    async def test_product_not_found_returns_error(self):
        """Verify error message when product is not found."""
        from app.graphql.common.services.overage_service import OverageService

        session = AsyncMock()
        # Mock execute to return None for product query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        service = OverageService(session)

        result = await service.find_effective_commission_rate_and_overage(
            product_id=uuid4(),
            detail_unit_price=100.0,
            factory_id=uuid4(),
            end_user_id=uuid4(),
            quantity=1.0,
        )

        assert result.success is False
        assert "not found" in result.error_message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
