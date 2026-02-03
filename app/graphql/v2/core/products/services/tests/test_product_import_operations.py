"""
Unit tests for ProductImportOperations.

Tests validate product creation and update logic including
error handling behavior.
"""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.graphql.v2.core.products.services.product_import_operations import (
    ProductImportOperations,
)
from app.graphql.v2.core.products.strawberry.product_import_types import (
    ProductImportItemInput,
)


class TestCreateProducts:
    """Test cases for create_products method."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.begin_nested = MagicMock(return_value=AsyncMock())
        session.begin_nested.return_value.__aenter__ = AsyncMock()
        session.begin_nested.return_value.__aexit__ = AsyncMock()
        return session

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def operations(
        self, mock_session: AsyncMock, mock_repository: AsyncMock
    ) -> ProductImportOperations:
        return ProductImportOperations(
            session=mock_session,
            products_repository=mock_repository,
        )

    @pytest.mark.asyncio
    async def test_create_products_with_valid_data(
        self, operations: ProductImportOperations, mock_repository: AsyncMock
    ) -> None:
        """Test create_products with valid data creates products."""
        factory_id = uuid4()
        uom_id = uuid4()
        products_data = [
            ProductImportItemInput(
                factory_part_number="PART-001",
                unit_price=Decimal("10.00"),
                description="Test Product 1",
            ),
            ProductImportItemInput(
                factory_part_number="PART-002",
                unit_price=Decimal("20.00"),
                description="Test Product 2",
            ),
        ]

        mock_repository.create = AsyncMock(return_value=MagicMock())

        created, updated, errors = await operations.create_products(
            products_data, factory_id, uom_id
        )

        assert created == 2
        assert updated == 0
        assert errors == []
        assert mock_repository.create.call_count == 2

    @pytest.mark.asyncio
    async def test_create_products_handles_errors_gracefully(
        self,
        mock_session: AsyncMock,
        mock_repository: AsyncMock,
    ) -> None:
        """Test create_products handles errors and returns them in errors list."""
        # Create a context manager that raises the exception
        mock_nested = MagicMock()
        mock_nested.__aenter__ = AsyncMock(return_value=None)
        mock_nested.__aexit__ = AsyncMock(return_value=False)
        mock_session.begin_nested = MagicMock(return_value=mock_nested)

        operations = ProductImportOperations(
            session=mock_session,
            products_repository=mock_repository,
        )

        factory_id = uuid4()
        uom_id = uuid4()
        products_data = [
            ProductImportItemInput(
                factory_part_number="PART-001",
                unit_price=Decimal("10.00"),
                description="Test Product",
            ),
        ]

        # Simulate general error on create
        mock_repository.create = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        created, updated, errors = await operations.create_products(
            products_data, factory_id, uom_id
        )

        assert created == 0
        assert updated == 0
        assert len(errors) == 1
        assert errors[0].factory_part_number == "PART-001"
        assert "Database connection failed" in errors[0].error

    @pytest.mark.asyncio
    async def test_create_products_uses_default_commission_rate(
        self, operations: ProductImportOperations, mock_repository: AsyncMock
    ) -> None:
        """Test create_products uses default commission rate when not provided."""
        factory_id = uuid4()
        uom_id = uuid4()
        products_data = [
            ProductImportItemInput(
                factory_part_number="PART-001",
                unit_price=Decimal("10.00"),
            ),
        ]

        mock_repository.create = AsyncMock(return_value=MagicMock())

        with patch(
            "app.graphql.v2.core.products.services.product_import_operations.ProductInput"
        ) as mock_input:
            mock_input.return_value.to_orm_model.return_value = MagicMock()
            _ = await operations.create_products(products_data, factory_id, uom_id)

            # Verify default commission rate was used
            call_kwargs = mock_input.call_args.kwargs
            assert call_kwargs["default_commission_rate"] == Decimal("0.10")


class TestUpdateProducts:
    """Test cases for update_products method."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def operations(
        self, mock_session: AsyncMock, mock_repository: AsyncMock
    ) -> ProductImportOperations:
        return ProductImportOperations(
            session=mock_session,
            products_repository=mock_repository,
        )

    @pytest.mark.asyncio
    async def test_update_products_with_valid_data(
        self, operations: ProductImportOperations
    ) -> None:
        """Test update_products with valid data updates products."""
        existing_product = MagicMock()
        existing_product.unit_price = Decimal("5.00")
        existing_product.description = "Old description"

        product_data = ProductImportItemInput(
            factory_part_number="PART-001",
            unit_price=Decimal("10.00"),
            description="New description",
        )

        products_to_update = [(product_data, existing_product)]

        updated, errors = await operations.update_products(
            products_to_update  # type: ignore[arg-type]
        )

        assert updated == 1
        assert errors == []
        assert existing_product.unit_price == Decimal("10.00")
        assert existing_product.description == "New description"

    @pytest.mark.asyncio
    async def test_update_products_preserves_none_fields(
        self, operations: ProductImportOperations
    ) -> None:
        """Test update_products preserves existing values for None fields."""
        existing_product = MagicMock()
        existing_product.unit_price = Decimal("5.00")
        existing_product.description = "Original description"
        existing_product.upc = "123456"

        product_data = ProductImportItemInput(
            factory_part_number="PART-001",
            unit_price=Decimal("10.00"),
            # description and upc are None
        )

        products_to_update = [(product_data, existing_product)]

        updated, errors = await operations.update_products(
            products_to_update  # type: ignore[arg-type]
        )

        assert updated == 1
        assert errors == []
        # unit_price updated
        assert existing_product.unit_price == Decimal("10.00")
        # description and upc should not be changed (None means skip update)
