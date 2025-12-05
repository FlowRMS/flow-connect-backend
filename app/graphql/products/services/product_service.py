from uuid import UUID

from commons.auth import AuthInfo
from commons.db.models import Product

from app.graphql.links.models.entity_type import EntityType
from app.graphql.products.repositories.products_repository import ProductsRepository


class ProductService:
    """Service for Products entity business logic."""

    def __init__(
        self,
        repository: ProductsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def search_products(
        self, search_term: str, factory_id: UUID | None, limit: int = 20
    ) -> list[Product]:
        """
        Search products by factory part number.

        Args:
            search_term: The search term to match against factory part number
            factory_id: The UUID of the factory to filter products by (optional)
            limit: Maximum number of products to return (default: 20)

        Returns:
            List of Product objects matching the search criteria
        """
        return await self.repository.search_by_fpn(search_term, factory_id, limit)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Product]:
        """Find all products linked to a specific entity."""
        return await self.repository.find_by_entity(entity_type, entity_id)
