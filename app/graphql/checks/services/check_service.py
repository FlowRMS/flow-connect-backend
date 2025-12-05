from uuid import UUID

from commons.auth import AuthInfo
from commons.db.models import Check

from app.graphql.checks.repositories.checks_repository import ChecksRepository
from app.graphql.links.models.entity_type import EntityType


class CheckService:
    """Service for Checks entity business logic."""

    def __init__(
        self,
        repository: ChecksRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def search_checks(self, search_term: str, limit: int = 20) -> list[Check]:
        """
        Search checks by check number.

        Args:
            search_term: The search term to match against check number
            limit: Maximum number of checks to return (default: 20)

        Returns:
            List of Check objects matching the search criteria
        """
        return await self.repository.search_by_check_number(search_term, limit)

    async def find_checks_by_job_id(self, job_id: UUID) -> list[Check]:
        """Find all checks linked to the given job ID."""
        return await self.repository.find_by_job_id(job_id)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Check]:
        """Find all checks linked to a specific entity."""
        return await self.repository.find_by_entity(entity_type, entity_id)
