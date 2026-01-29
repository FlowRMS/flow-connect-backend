"""GraphQL mutations for product import."""

from uuid import UUID

import strawberry
from aioinject import Injected
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.inject import inject
from app.graphql.v2.core.products.repositories.product_cpn_repository import (
    ProductCpnRepository,
)
from app.graphql.v2.core.products.repositories.product_quantity_pricing_repository import (
    ProductQuantityPricingRepository,
)
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.products.services.product_import_service import (
    ProductImportService,
)
from app.graphql.v2.core.products.strawberry.product_import_types import (
    ProductImportInput,
    ProductImportResult,
)


@strawberry.type
class ProductImportMutations:
    """GraphQL mutations for bulk product import."""

    @strawberry.mutation
    @inject
    async def import_products(
        self,
        input: ProductImportInput,
        default_uom_id: UUID,
        session: Injected[AsyncSession],
        products_repository: Injected[ProductsRepository],
        quantity_pricing_repository: Injected[ProductQuantityPricingRepository],
        cpn_repository: Injected[ProductCpnRepository],
    ) -> ProductImportResult:
        """
        Import products from normalized data.

        This mutation handles bulk import of products with:
        - Automatic create/update based on factory_part_number
        - Quantity pricing bands
        - Customer-specific pricing (CPNs) by customer name lookup
        - Non-destructive updates (won't overwrite with null)

        Args:
            input: The import data containing factory_id and list of products
            default_uom_id: Default Unit of Measure ID to use for new products

        Returns:
            ProductImportResult with counts and any errors
        """
        service = ProductImportService(
            session=session,
            products_repository=products_repository,
            quantity_pricing_repository=quantity_pricing_repository,
            cpn_repository=cpn_repository,
        )
        return await service.import_products(input, default_uom_id)
