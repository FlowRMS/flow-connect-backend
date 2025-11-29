"""Service for PreOpportunity entity business logic."""

from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.pre_opportunities.models.pre_opportunity_model import PreOpportunity
from app.graphql.pre_opportunities.repositories.pre_opportunities_repository import (
    PreOpportunitiesRepository,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_input import (
    PreOpportunityInput,
)


class PreOpportunitiesService:
    """Service for PreOpportunity entity business logic."""

    def __init__(
        self,
        repository: PreOpportunitiesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def create_pre_opportunity(
        self, pre_opportunity_input: PreOpportunityInput
    ) -> PreOpportunity:
        """
        Create a new pre-opportunity with balance calculation.

        Args:
            pre_opportunity_input: Input data for the pre-opportunity

        Returns:
            Created pre-opportunity entity
        """
        pre_opportunity = pre_opportunity_input.to_orm_model()
        return await self.repository.create_with_balance(pre_opportunity)

    async def update_pre_opportunity(
        self, pre_opportunity_input: PreOpportunityInput
    ) -> PreOpportunity:
        """
        Update a pre-opportunity and recalculate balance.

        Args:
            pre_opportunity_input: Input data for the pre-opportunity

        Returns:
            Updated pre-opportunity entity
        """
        pre_opportunity = pre_opportunity_input.to_orm_model()
        if pre_opportunity_input.id is None:
            raise ValueError("ID must be provided for update")

        pre_opportunity.id = pre_opportunity_input.id
        return await self.repository.update_with_balance(pre_opportunity)

    async def get_pre_opportunity(
        self, pre_opportunity_id: UUID | str
    ) -> PreOpportunity:
        """Get a pre-opportunity by ID."""
        pre_opportunity = await self.repository.get_by_id(pre_opportunity_id)
        if not pre_opportunity:
            raise NotFoundError(str(pre_opportunity_id))
        return pre_opportunity

    async def delete_pre_opportunity(self, pre_opportunity_id: UUID | str) -> bool:
        """Delete a pre-opportunity by ID."""
        if not await self.repository.exists(pre_opportunity_id):
            raise NotFoundError(str(pre_opportunity_id))
        return await self.repository.delete(pre_opportunity_id)

    async def get_by_job_id(self, job_id: UUID) -> list[PreOpportunity]:
        """Get all pre-opportunities for a specific job."""
        return await self.repository.get_by_job_id(job_id)

    async def get_by_customer_id(self, customer_id: UUID) -> list[PreOpportunity]:
        """Get all pre-opportunities for a specific customer."""
        return await self.repository.get_by_customer_id(customer_id)
