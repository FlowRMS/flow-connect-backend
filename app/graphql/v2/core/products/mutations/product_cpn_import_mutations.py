"""GraphQL mutations for product CPN bulk import."""

import strawberry
from aioinject import Injected
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.inject import inject
from app.graphql.v2.core.products.repositories.product_cpn_repository import (
    ProductCpnRepository,
)
from app.graphql.v2.core.products.repositories.products_repository import (
    ProductsRepository,
)
from app.graphql.v2.core.products.services.product_cpn_import_service import (
    ProductCpnImportService,
)
from app.graphql.v2.core.products.strawberry.product_cpn_import_types import (
    ProductCpnImportInput,
    ProductCpnImportResult,
)


@strawberry.type
class ProductCpnImportMutations:
    """GraphQL mutations for bulk CPN import."""

    @strawberry.mutation
    @inject
    async def import_product_cpns(
        self,
        input: ProductCpnImportInput,
        session: Injected[AsyncSession],
        products_repository: Injected[ProductsRepository],
        cpn_repository: Injected[ProductCpnRepository],
    ) -> ProductCpnImportResult:
        """
        Import customer-specific pricing (CPNs) from normalized data.

        This mutation handles bulk import of CPNs with:
        - Product lookup by factory_part_number + factory_id
        - Customer lookup by company_name
        - Automatic create/update based on product_id + customer_id

        Args:
            input: The import data containing factory_id and list of CPNs

        Returns:
            ProductCpnImportResult with counts and any errors
        """
        service = ProductCpnImportService(
            session=session,
            products_repository=products_repository,
            cpn_repository=cpn_repository,
        )
        return await service.import_cpns(input)
