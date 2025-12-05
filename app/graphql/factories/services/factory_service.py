from uuid import UUID

from commons.auth import AuthInfo
from commons.db.models import Factory

from app.graphql.factories.repositories.factories_repository import FactoriesRepository
from app.graphql.links.models.entity_type import EntityType


class FactoryService:
    """Service for Factories entity business logic."""

    def __init__(
        self,
        repository: FactoriesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def search_factories(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Factory]:
        """
        Search factories by title.

        Args:
            search_term: The search term to match against title
            published: Filter by published status (default: True)
            limit: Maximum number of factories to return (default: 20)

        Returns:
            List of Factory objects matching the search criteria
        """
        return await self.repository.search_by_title(search_term, published, limit)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Factory]:
        """Find all factories linked to a specific entity."""
        return await self.repository.find_by_entity(entity_type, entity_id)
