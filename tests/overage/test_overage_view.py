#!/usr/bin/env python3
"""
Unit tests for Overage View calculations.

Tests the overage calculation logic with various scenarios:
1. Factory with overage_allowed=true (BY_LINE mode)
2. Factory with overage_allowed=false
3. Different price scenarios (markup, at-cost, below-cost)
4. Rep share calculations

These tests use mocks and don't require a running server.

Usage:
    cd /home/jorge/flowrms/FLO-727/flow-py-backend
    uv run pytest tests/overage/test_overage_view.py -v
"""
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, PropertyMock
from uuid import uuid4

# Check if required modules are available
try:
    from commons.db.v6.core.factories import Factory, OverageTypeEnum
    from commons.db.v6.core.products import Product, ProductCpn
    from app.graphql.common.services.overage_service import OverageService
    from app.graphql.common.strawberry.overage_record import (
        OverageRecord,
        OverageTypeEnum as GqlOverageTypeEnum,
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    MODULES_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not MODULES_AVAILABLE,
    reason="Required modules not available"
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    session = AsyncMock()
    return session


@pytest.fixture
def product_with_price():
    """Create a product with unit_price and commission rate."""
    product = MagicMock(spec=Product)
    product.id = uuid4()
    product.unit_price = Decimal("100.00")
    product.default_commission_rate = Decimal("10.00")
    return product


@pytest.fixture
def factory_overage_enabled():
    """Create a factory with overage enabled (BY_LINE mode)."""
    factory = MagicMock(spec=Factory)
    factory.id = uuid4()
    factory.title = "Test Factory (Overage Enabled)"
    factory.overage_allowed = True
    factory.overage_type = OverageTypeEnum.BY_LINE
    factory.rep_overage_share = Decimal("100.00")  # 100% to rep
    factory.base_commission_rate = Decimal("8.00")
    return factory


@pytest.fixture
def factory_overage_disabled():
    """Create a factory with overage disabled."""
    factory = MagicMock(spec=Factory)
    factory.id = uuid4()
    factory.title = "Test Factory (Overage Disabled)"
    factory.overage_allowed = False
    factory.overage_type = OverageTypeEnum.BY_LINE
    factory.rep_overage_share = Decimal("0.00")
    factory.base_commission_rate = Decimal("8.00")
    return factory


@pytest.fixture
def factory_by_total():
    """Create a factory with BY_TOTAL overage mode."""
    factory = MagicMock(spec=Factory)
    factory.id = uuid4()
    factory.title = "Test Factory (BY_TOTAL)"
    factory.overage_allowed = True
    factory.overage_type = OverageTypeEnum.BY_TOTAL
    factory.rep_overage_share = Decimal("50.00")  # 50% to rep
    factory.base_commission_rate = Decimal("8.00")
    return factory


# ============================================================================
# Test Overage Enabled - BY_LINE Mode
# ============================================================================

class TestOverageEnabledByLine:
    """Test scenarios where factory has overage_allowed=true and BY_LINE mode."""

    @pytest.mark.asyncio
    async def test_markup_generates_overage(
        self, mock_session, product_with_price, factory_overage_enabled
    ):
        """When detail_unit_price > base_unit_price, overage should be calculated."""
        # Setup mocks
        product_result = MagicMock()
        product_result.scalar_one_or_none.return_value = product_with_price

        factory_result = MagicMock()
        factory_result.scalar_one_or_none.return_value = factory_overage_enabled

        cpn_result = MagicMock()
        cpn_result.scalar_one_or_none.return_value = None  # No customer-specific pricing

        qty_result = MagicMock()
        qty_result.scalar_one_or_none.return_value = None  # No quantity pricing

        # Return different results for different queries
        mock_session.execute.side_effect = [
            product_result,
            factory_result,
            cpn_result,
            qty_result,
        ]

        service = OverageService(mock_session)

        # Sell at 20% markup
        base_price = 100.00
        detail_price = 120.00  # $20 markup

        result = await service.find_effective_commission_rate_and_overage(
            product_id=product_with_price.id,
            detail_unit_price=detail_price,
            factory_id=factory_overage_enabled.id,
            end_user_id=uuid4(),
            quantity=1.0,
        )

        assert result.success is True
        assert result.overage_unit_price == 20.00  # $120 - $100 = $20 overage
        assert result.base_unit_price == 100.00
        assert result.overage_type == GqlOverageTypeEnum.BY_LINE
        assert result.rep_share == 1.0  # 100%

    @pytest.mark.asyncio
    async def test_no_overage_when_at_base_price(
        self, mock_session, product_with_price, factory_overage_enabled
    ):
        """When detail_unit_price == base_unit_price, no overage."""
        product_result = MagicMock()
        product_result.scalar_one_or_none.return_value = product_with_price

        factory_result = MagicMock()
        factory_result.scalar_one_or_none.return_value = factory_overage_enabled

        cpn_result = MagicMock()
        cpn_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [
            product_result,
            factory_result,
            cpn_result,
        ]

        service = OverageService(mock_session)

        result = await service.find_effective_commission_rate_and_overage(
            product_id=product_with_price.id,
            detail_unit_price=100.00,  # Same as base
            factory_id=factory_overage_enabled.id,
            end_user_id=uuid4(),
            quantity=1.0,
        )

        assert result.success is True
        assert result.overage_unit_price is None
        assert result.base_unit_price == 100.00

    @pytest.mark.asyncio
    async def test_no_overage_when_below_base_price(
        self, mock_session, product_with_price, factory_overage_enabled
    ):
        """When detail_unit_price < base_unit_price, no overage (discount)."""
        product_result = MagicMock()
        product_result.scalar_one_or_none.return_value = product_with_price

        factory_result = MagicMock()
        factory_result.scalar_one_or_none.return_value = factory_overage_enabled

        cpn_result = MagicMock()
        cpn_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [
            product_result,
            factory_result,
            cpn_result,
        ]

        service = OverageService(mock_session)

        result = await service.find_effective_commission_rate_and_overage(
            product_id=product_with_price.id,
            detail_unit_price=80.00,  # 20% discount
            factory_id=factory_overage_enabled.id,
            end_user_id=uuid4(),
            quantity=1.0,
        )

        assert result.success is True
        assert result.overage_unit_price is None


# ============================================================================
# Test Overage Disabled
# ============================================================================

class TestOverageDisabled:
    """Test scenarios where factory has overage_allowed=false."""

    @pytest.mark.asyncio
    async def test_no_overage_when_disabled(
        self, mock_session, product_with_price, factory_overage_disabled
    ):
        """When overage_allowed=false, no overage calculation even with markup."""
        product_result = MagicMock()
        product_result.scalar_one_or_none.return_value = product_with_price

        factory_result = MagicMock()
        factory_result.scalar_one_or_none.return_value = factory_overage_disabled

        cpn_result = MagicMock()
        cpn_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [
            product_result,
            factory_result,
            cpn_result,
        ]

        service = OverageService(mock_session)

        result = await service.find_effective_commission_rate_and_overage(
            product_id=product_with_price.id,
            detail_unit_price=150.00,  # 50% markup - but overage disabled
            factory_id=factory_overage_disabled.id,
            end_user_id=uuid4(),
            quantity=1.0,
        )

        assert result.success is True
        assert result.overage_unit_price is None  # No overage calculated
        assert result.rep_share is None
        # Should still return commission rate
        assert result.effective_commission_rate is not None


# ============================================================================
# Test BY_TOTAL Mode
# ============================================================================

class TestByTotalMode:
    """Test scenarios with BY_TOTAL overage mode."""

    @pytest.mark.asyncio
    async def test_by_total_returns_error_for_line_calc(
        self, mock_session, product_with_price, factory_by_total
    ):
        """BY_TOTAL mode should return error when called per-line."""
        product_result = MagicMock()
        product_result.scalar_one_or_none.return_value = product_with_price

        factory_result = MagicMock()
        factory_result.scalar_one_or_none.return_value = factory_by_total

        cpn_result = MagicMock()
        cpn_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [
            product_result,
            factory_result,
            cpn_result,
        ]

        service = OverageService(mock_session)

        result = await service.find_effective_commission_rate_and_overage(
            product_id=product_with_price.id,
            detail_unit_price=120.00,
            factory_id=factory_by_total.id,
            end_user_id=uuid4(),
            quantity=1.0,
        )

        assert result.success is False
        assert "BY_TOTAL" in result.error_message


# ============================================================================
# Test Rep Share Calculations
# ============================================================================

class TestRepShareCalculations:
    """Test rep_overage_share percentage calculations."""

    @pytest.mark.asyncio
    async def test_full_rep_share(
        self, mock_session, product_with_price, factory_overage_enabled
    ):
        """Test 100% rep share calculation."""
        factory_overage_enabled.rep_overage_share = Decimal("100.00")

        product_result = MagicMock()
        product_result.scalar_one_or_none.return_value = product_with_price

        factory_result = MagicMock()
        factory_result.scalar_one_or_none.return_value = factory_overage_enabled

        cpn_result = MagicMock()
        cpn_result.scalar_one_or_none.return_value = None

        qty_result = MagicMock()
        qty_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [
            product_result,
            factory_result,
            cpn_result,
            qty_result,
        ]

        service = OverageService(mock_session)

        result = await service.find_effective_commission_rate_and_overage(
            product_id=product_with_price.id,
            detail_unit_price=120.00,
            factory_id=factory_overage_enabled.id,
            end_user_id=uuid4(),
            quantity=1.0,
        )

        assert result.rep_share == 1.0  # 100%

    @pytest.mark.asyncio
    async def test_partial_rep_share(
        self, mock_session, product_with_price, factory_overage_enabled
    ):
        """Test 50% rep share calculation."""
        factory_overage_enabled.rep_overage_share = Decimal("50.00")

        product_result = MagicMock()
        product_result.scalar_one_or_none.return_value = product_with_price

        factory_result = MagicMock()
        factory_result.scalar_one_or_none.return_value = factory_overage_enabled

        cpn_result = MagicMock()
        cpn_result.scalar_one_or_none.return_value = None

        qty_result = MagicMock()
        qty_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [
            product_result,
            factory_result,
            cpn_result,
            qty_result,
        ]

        service = OverageService(mock_session)

        result = await service.find_effective_commission_rate_and_overage(
            product_id=product_with_price.id,
            detail_unit_price=120.00,
            factory_id=factory_overage_enabled.id,
            end_user_id=uuid4(),
            quantity=1.0,
        )

        assert result.rep_share == 0.5  # 50%


# ============================================================================
# Test Frontend Expected Values
# ============================================================================

class TestFrontendExpectedValues:
    """Test that response contains all fields expected by frontend Overage View."""

    @pytest.mark.asyncio
    async def test_overage_record_has_all_frontend_fields(
        self, mock_session, product_with_price, factory_overage_enabled
    ):
        """Verify OverageRecord has all fields the frontend expects."""
        product_result = MagicMock()
        product_result.scalar_one_or_none.return_value = product_with_price

        factory_result = MagicMock()
        factory_result.scalar_one_or_none.return_value = factory_overage_enabled

        cpn_result = MagicMock()
        cpn_result.scalar_one_or_none.return_value = None

        qty_result = MagicMock()
        qty_result.scalar_one_or_none.return_value = None

        mock_session.execute.side_effect = [
            product_result,
            factory_result,
            cpn_result,
            qty_result,
        ]

        service = OverageService(mock_session)

        result = await service.find_effective_commission_rate_and_overage(
            product_id=product_with_price.id,
            detail_unit_price=120.00,
            factory_id=factory_overage_enabled.id,
            end_user_id=uuid4(),
            quantity=1.0,
        )

        # Frontend expects these fields for Overage View columns
        assert hasattr(result, 'effective_commission_rate')  # Eff Rate %
        assert hasattr(result, 'overage_unit_price')  # Ovg $
        assert hasattr(result, 'base_unit_price')  # Base price
        assert hasattr(result, 'rep_share')  # Rep's share of overage
        assert hasattr(result, 'overage_type')  # BY_LINE or BY_TOTAL
        assert hasattr(result, 'success')  # Error handling
        assert hasattr(result, 'error_message')  # Error message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
