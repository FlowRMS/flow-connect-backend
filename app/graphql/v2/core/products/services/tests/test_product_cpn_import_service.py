from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.graphql.v2.core.products.services.product_cpn_import_service import (
    ProductCpnImportService,
)
from app.graphql.v2.core.products.strawberry.product_cpn_import_input import (
    ProductCpnImportInput,
)
from app.graphql.v2.core.products.strawberry.product_cpn_import_item_input import (
    ProductCpnImportItemInput,
)


class TestImportCpns:
    """Test cases for import_cpns method."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        session = AsyncMock()
        session.begin_nested = MagicMock(return_value=AsyncMock())
        session.begin_nested.return_value.__aenter__ = AsyncMock()
        session.begin_nested.return_value.__aexit__ = AsyncMock()
        session.add = MagicMock()
        session.flush = AsyncMock()
        return session

    @pytest.fixture
    def mock_products_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_cpn_repository(self) -> AsyncMock:
        repo = AsyncMock()
        repo.find_existing_cpns = AsyncMock(return_value={})
        return repo

    @pytest.fixture
    def mock_customers_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def service(
        self,
        mock_session: AsyncMock,
        mock_products_repository: AsyncMock,
        mock_cpn_repository: AsyncMock,
        mock_customers_repository: AsyncMock,
    ) -> ProductCpnImportService:
        return ProductCpnImportService(
            session=mock_session,
            products_repository=mock_products_repository,
            cpn_repository=mock_cpn_repository,
            customers_repository=mock_customers_repository,
        )

    @pytest.mark.asyncio
    async def test_import_cpns_with_valid_data_creates_cpns(
        self,
        service: ProductCpnImportService,
        mock_products_repository: AsyncMock,
        mock_customers_repository: AsyncMock,
        mock_cpn_repository: AsyncMock,
    ) -> None:
        """Test import_cpns with valid data creates CPNs."""
        factory_id = uuid4()
        product_id = uuid4()
        customer_id = uuid4()

        # Mock product lookup
        product = MagicMock()
        product.id = product_id
        product.factory_part_number = "PART-001"
        mock_products_repository.get_existing_products.return_value = [product]

        # Mock customer lookup
        customer = MagicMock()
        customer.id = customer_id
        mock_customers_repository.get_by_company_names.return_value = {
            "Customer A": customer
        }

        # No existing CPNs
        mock_cpn_repository.find_existing_cpns.return_value = {}

        import_input = ProductCpnImportInput(
            factory_id=factory_id,
            cpns=[
                ProductCpnImportItemInput(
                    factory_part_number="PART-001",
                    customer_name="Customer A",
                    customer_part_number="CPN-001",
                    unit_price=Decimal("50.00"),
                    commission_rate=Decimal("0.15"),
                ),
            ],
        )

        result = await service.import_cpns(import_input)

        assert result.success is True
        assert result.cpns_created == 1
        assert result.cpns_updated == 0
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_import_cpns_with_missing_products_returns_errors(
        self,
        service: ProductCpnImportService,
        mock_products_repository: AsyncMock,
        mock_customers_repository: AsyncMock,
    ) -> None:
        """Test import_cpns with missing products returns errors."""
        factory_id = uuid4()

        # No products found
        mock_products_repository.get_existing_products.return_value = []

        # Customer exists
        customer = MagicMock()
        customer.id = uuid4()
        mock_customers_repository.get_by_company_names.return_value = {
            "Customer A": customer
        }

        import_input = ProductCpnImportInput(
            factory_id=factory_id,
            cpns=[
                ProductCpnImportItemInput(
                    factory_part_number="UNKNOWN-PART",
                    customer_name="Customer A",
                    customer_part_number="CPN-001",
                    unit_price=Decimal("50.00"),
                    commission_rate=Decimal("0.15"),
                ),
            ],
        )

        result = await service.import_cpns(import_input)

        assert result.success is False
        assert result.cpns_created == 0
        assert len(result.errors) == 1
        assert "Product not found" in result.errors[0].error
        assert "UNKNOWN-PART" in result.products_not_found

    @pytest.mark.asyncio
    async def test_import_cpns_with_missing_customers_returns_errors(
        self,
        service: ProductCpnImportService,
        mock_products_repository: AsyncMock,
        mock_customers_repository: AsyncMock,
    ) -> None:
        """Test import_cpns with missing customers returns errors."""
        factory_id = uuid4()
        product_id = uuid4()

        # Product exists
        product = MagicMock()
        product.id = product_id
        product.factory_part_number = "PART-001"
        mock_products_repository.get_existing_products.return_value = [product]

        # No customers found
        mock_customers_repository.get_by_company_names.return_value = {}

        import_input = ProductCpnImportInput(
            factory_id=factory_id,
            cpns=[
                ProductCpnImportItemInput(
                    factory_part_number="PART-001",
                    customer_name="Unknown Customer",
                    customer_part_number="CPN-001",
                    unit_price=Decimal("50.00"),
                    commission_rate=Decimal("0.15"),
                ),
            ],
        )

        result = await service.import_cpns(import_input)

        assert result.success is False
        assert result.cpns_created == 0
        assert len(result.errors) == 1
        assert "Customer not found" in result.errors[0].error
        assert "Unknown Customer" in result.customers_not_found

    @pytest.mark.asyncio
    async def test_import_cpns_deduplication_keeps_last_occurrence(
        self,
        service: ProductCpnImportService,
        mock_products_repository: AsyncMock,
        mock_customers_repository: AsyncMock,
        mock_cpn_repository: AsyncMock,
    ) -> None:
        """Test import_cpns deduplication keeps last occurrence."""
        factory_id = uuid4()
        product_id = uuid4()
        customer_id = uuid4()

        # Mock product lookup
        product = MagicMock()
        product.id = product_id
        product.factory_part_number = "PART-001"
        mock_products_repository.get_existing_products.return_value = [product]

        # Mock customer lookup
        customer = MagicMock()
        customer.id = customer_id
        mock_customers_repository.get_by_company_names.return_value = {
            "Customer A": customer
        }

        # No existing CPNs
        mock_cpn_repository.find_existing_cpns.return_value = {}

        # Duplicate entries - last one should win
        import_input = ProductCpnImportInput(
            factory_id=factory_id,
            cpns=[
                ProductCpnImportItemInput(
                    factory_part_number="PART-001",
                    customer_name="Customer A",
                    customer_part_number="CPN-OLD",
                    unit_price=Decimal("40.00"),
                    commission_rate=Decimal("0.10"),
                ),
                ProductCpnImportItemInput(
                    factory_part_number="PART-001",
                    customer_name="Customer A",
                    customer_part_number="CPN-NEW",
                    unit_price=Decimal("50.00"),
                    commission_rate=Decimal("0.15"),
                ),
            ],
        )

        result = await service.import_cpns(import_input)

        # Only 1 CPN created (deduplicated)
        assert result.cpns_created == 1
        assert result.cpns_updated == 0

    @pytest.mark.asyncio
    async def test_import_cpns_empty_list_returns_early(
        self,
        service: ProductCpnImportService,
        mock_products_repository: AsyncMock,
    ) -> None:
        """Test import_cpns with empty list returns early."""
        factory_id = uuid4()

        import_input = ProductCpnImportInput(
            factory_id=factory_id,
            cpns=[],
        )

        result = await service.import_cpns(import_input)

        assert result.success is True
        assert result.cpns_created == 0
        assert result.cpns_updated == 0
        assert result.message == "No CPNs to import"
        # Should not call repository
        mock_products_repository.get_existing_products.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_cpns_updates_existing_cpns(
        self,
        service: ProductCpnImportService,
        mock_products_repository: AsyncMock,
        mock_customers_repository: AsyncMock,
        mock_cpn_repository: AsyncMock,
    ) -> None:
        """Test import_cpns updates existing CPNs."""
        factory_id = uuid4()
        product_id = uuid4()
        customer_id = uuid4()

        # Mock product lookup
        product = MagicMock()
        product.id = product_id
        product.factory_part_number = "PART-001"
        mock_products_repository.get_existing_products.return_value = [product]

        # Mock customer lookup
        customer = MagicMock()
        customer.id = customer_id
        mock_customers_repository.get_by_company_names.return_value = {
            "Customer A": customer
        }

        # Existing CPN
        existing_cpn = MagicMock()
        existing_cpn.unit_price = Decimal("40.00")
        existing_cpn.commission_rate = Decimal("0.10")
        mock_cpn_repository.find_existing_cpns.return_value = {
            (product_id, customer_id): existing_cpn
        }

        import_input = ProductCpnImportInput(
            factory_id=factory_id,
            cpns=[
                ProductCpnImportItemInput(
                    factory_part_number="PART-001",
                    customer_name="Customer A",
                    customer_part_number="CPN-UPDATED",
                    unit_price=Decimal("50.00"),
                    commission_rate=Decimal("0.15"),
                ),
            ],
        )

        result = await service.import_cpns(import_input)

        assert result.success is True
        assert result.cpns_created == 0
        assert result.cpns_updated == 1
        # Verify update was applied
        assert existing_cpn.unit_price == Decimal("50.00")
        assert existing_cpn.commission_rate == Decimal("0.15")
        assert existing_cpn.customer_part_number == "CPN-UPDATED"
