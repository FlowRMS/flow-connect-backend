from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.graphql.v2.core.products.services.product_pricing_operations import (
    ProductPricingOperations,
)
from app.graphql.v2.core.products.strawberry.product_import_types import (
    CustomerPricingImportInput,
    QuantityPricingImportInput,
)


class TestReplaceQuantityPricing:
    """Test cases for replace_quantity_pricing method."""

    @pytest.fixture
    def mock_quantity_pricing_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_customers_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_cpn_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def operations(
        self,
        mock_quantity_pricing_repository: AsyncMock,
        mock_customers_repository: AsyncMock,
        mock_cpn_repository: AsyncMock,
    ) -> ProductPricingOperations:
        return ProductPricingOperations(
            quantity_pricing_repository=mock_quantity_pricing_repository,
            customers_repository=mock_customers_repository,
            cpn_repository=mock_cpn_repository,
        )

    @pytest.mark.asyncio
    async def test_replace_quantity_pricing_deletes_old_and_creates_new(
        self,
        operations: ProductPricingOperations,
        mock_quantity_pricing_repository: AsyncMock,
    ) -> None:
        """Test replace_quantity_pricing deletes existing and creates new bands."""
        product_id = uuid4()
        pricing_data = [
            QuantityPricingImportInput(
                quantity_low=Decimal("1"),
                quantity_high=Decimal("10"),
                unit_price=Decimal("100.00"),
            ),
            QuantityPricingImportInput(
                quantity_low=Decimal("11"),
                quantity_high=Decimal("50"),
                unit_price=Decimal("90.00"),
            ),
        ]

        created_count = await operations.replace_quantity_pricing(
            product_id, pricing_data
        )

        assert created_count == 2
        # Verify delete was called
        mock_quantity_pricing_repository.delete_by_product_id.assert_called_once_with(
            product_id
        )
        # Verify add_pricing was called for each band
        assert mock_quantity_pricing_repository.add_pricing.call_count == 2

    @pytest.mark.asyncio
    async def test_replace_quantity_pricing_uses_max_for_none_quantity_high(
        self,
        operations: ProductPricingOperations,
        mock_quantity_pricing_repository: AsyncMock,
    ) -> None:
        """Test replace_quantity_pricing uses MAX_QUANTITY_HIGH for None quantity_high."""
        product_id = uuid4()
        pricing_data = [
            QuantityPricingImportInput(
                quantity_low=Decimal("100"),
                quantity_high=None,  # "and above"
                unit_price=Decimal("80.00"),
            ),
        ]

        created_count = await operations.replace_quantity_pricing(
            product_id, pricing_data
        )

        assert created_count == 1
        # Verify the pricing was added with MAX_QUANTITY_HIGH
        call_args = mock_quantity_pricing_repository.add_pricing.call_args[0][0]
        assert call_args.quantity_high == ProductPricingOperations.MAX_QUANTITY_HIGH

    @pytest.mark.asyncio
    async def test_replace_quantity_pricing_empty_list(
        self,
        operations: ProductPricingOperations,
        mock_quantity_pricing_repository: AsyncMock,
    ) -> None:
        """Test replace_quantity_pricing with empty list only deletes."""
        product_id = uuid4()
        pricing_data: list[QuantityPricingImportInput] = []

        created_count = await operations.replace_quantity_pricing(
            product_id, pricing_data
        )

        assert created_count == 0
        # Delete should still be called
        mock_quantity_pricing_repository.delete_by_product_id.assert_called_once()
        # No adds
        assert mock_quantity_pricing_repository.add_pricing.call_count == 0


class TestProcessCustomerPricing:
    """Test cases for process_customer_pricing method."""

    @pytest.fixture
    def mock_quantity_pricing_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_customers_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_cpn_repository(self) -> AsyncMock:
        repo = AsyncMock()
        repo.find_existing_cpns = AsyncMock(return_value={})
        return repo

    @pytest.fixture
    def operations(
        self,
        mock_quantity_pricing_repository: AsyncMock,
        mock_customers_repository: AsyncMock,
        mock_cpn_repository: AsyncMock,
    ) -> ProductPricingOperations:
        return ProductPricingOperations(
            quantity_pricing_repository=mock_quantity_pricing_repository,
            customers_repository=mock_customers_repository,
            cpn_repository=mock_cpn_repository,
        )

    @pytest.mark.asyncio
    async def test_process_customer_pricing_creates_new_cpns(
        self,
        operations: ProductPricingOperations,
        mock_cpn_repository: AsyncMock,
    ) -> None:
        """Test process_customer_pricing creates new CPNs."""
        product_id = uuid4()
        customer_id = uuid4()
        customer = MagicMock()
        customer.id = customer_id

        customers_by_name: Any = {"Customer A": customer}
        pricing_data = [
            CustomerPricingImportInput(
                customer_name="Customer A",
                customer_part_number="CPN-001",
                unit_price=Decimal("50.00"),
                commission_rate=Decimal("0.15"),
            ),
        ]

        mock_cpn_repository.find_existing_cpns.return_value = {}

        created, updated, errors = await operations.process_customer_pricing(
            product_id, "PART-001", pricing_data, customers_by_name
        )

        assert created == 1
        assert updated == 0
        assert errors == []

    @pytest.mark.asyncio
    async def test_process_customer_pricing_updates_existing_cpns(
        self,
        operations: ProductPricingOperations,
        mock_cpn_repository: AsyncMock,
    ) -> None:
        """Test process_customer_pricing updates existing CPNs."""
        product_id = uuid4()
        customer_id = uuid4()
        customer = MagicMock()
        customer.id = customer_id

        existing_cpn = MagicMock()
        existing_cpn.unit_price = Decimal("40.00")
        existing_cpn.commission_rate = Decimal("0.10")

        customers_by_name: Any = {"Customer A": customer}
        pricing_data = [
            CustomerPricingImportInput(
                customer_name="Customer A",
                customer_part_number="CPN-001",
                unit_price=Decimal("50.00"),
                commission_rate=Decimal("0.15"),
            ),
        ]

        # Simulate existing CPN found
        mock_cpn_repository.find_existing_cpns.return_value = {
            (product_id, customer_id): existing_cpn
        }

        created, updated, errors = await operations.process_customer_pricing(
            product_id, "PART-001", pricing_data, customers_by_name
        )

        assert created == 0
        assert updated == 1
        assert errors == []
        assert existing_cpn.unit_price == Decimal("50.00")
        assert existing_cpn.commission_rate == Decimal("0.15")

    @pytest.mark.asyncio
    async def test_process_customer_pricing_skips_unknown_customers(
        self,
        operations: ProductPricingOperations,
        mock_cpn_repository: AsyncMock,
    ) -> None:
        """Test process_customer_pricing skips customers not in mapping."""
        product_id = uuid4()
        customers_by_name: Any = {}  # Empty - no customers found
        pricing_data = [
            CustomerPricingImportInput(
                customer_name="Unknown Customer",
                customer_part_number="CPN-001",
                unit_price=Decimal("50.00"),
                commission_rate=Decimal("0.15"),
            ),
        ]

        created, updated, errors = await operations.process_customer_pricing(
            product_id, "PART-001", pricing_data, customers_by_name
        )

        assert created == 0
        assert updated == 0
        assert errors == []
        # Should return early without calling cpn_repository
        mock_cpn_repository.find_existing_cpns.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_customer_pricing_empty_list_returns_zeros(
        self,
        operations: ProductPricingOperations,
        mock_cpn_repository: AsyncMock,
    ) -> None:
        """Test process_customer_pricing with empty list returns zeros."""
        product_id = uuid4()
        customers_by_name: Any = {}
        pricing_data: list[CustomerPricingImportInput] = []

        created, updated, errors = await operations.process_customer_pricing(
            product_id, "PART-001", pricing_data, customers_by_name
        )

        assert created == 0
        assert updated == 0
        assert errors == []
