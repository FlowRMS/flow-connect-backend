from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import AutoNumberEntityType
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.pre_opportunities.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)
from commons.db.v6.crm.pre_opportunities.pre_opportunity_model import PreOpportunity
from sqlalchemy.orm import joinedload, lazyload

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.auto_numbers.services.auto_number_settings_service import (
    AutoNumberSettingsService,
)
from app.graphql.pre_opportunities.repositories.pre_opportunities_repository import (
    PreOpportunitiesRepository,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_input import (
    PreOpportunityInput,
)


class PreOpportunitiesService:
    def __init__(
        self,
        repository: PreOpportunitiesRepository,
        auto_number_settings_service: AutoNumberSettingsService,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auto_number_settings_service = auto_number_settings_service
        self.auth_info = auth_info

    async def create_pre_opportunity(
        self, pre_opportunity_input: PreOpportunityInput
    ) -> PreOpportunity:
        if self.auto_number_settings_service.needs_generation(
            pre_opportunity_input.entity_number
        ):
            pre_opportunity_input.entity_number = (
                await self.auto_number_settings_service.generate_number(
                    AutoNumberEntityType.PRE_OPPORTUNITY
                )
            )

        if await self.repository.entity_number_exists(
            pre_opportunity_input.entity_number
        ):
            raise NameAlreadyExistsError(pre_opportunity_input.entity_number)

        pre_opportunity = await self.repository.create_with_balance(
            pre_opportunity_input.to_orm_model()
        )
        return await self.get_pre_opportunity(
            pre_opportunity.id,
        )

    async def update_pre_opportunity(
        self, pre_opportunity_input: PreOpportunityInput
    ) -> PreOpportunity:
        pre_opportunity = pre_opportunity_input.to_orm_model()
        if pre_opportunity_input.id is None:
            raise ValueError("ID must be provided for update")

        pre_opportunity.id = pre_opportunity_input.id
        _ = await self.repository.update_with_balance(pre_opportunity)
        return await self.get_pre_opportunity(
            pre_opportunity.id,
        )

    async def get_pre_opportunity(
        self, pre_opportunity_id: UUID | str
    ) -> PreOpportunity:
        pre_opportunity = await self.repository.get_by_id(
            pre_opportunity_id,
            options=[
                joinedload(PreOpportunity.created_by),
                joinedload(PreOpportunity.job),
                joinedload(PreOpportunity.balance),
                joinedload(PreOpportunity.details),
                joinedload(PreOpportunity.details).joinedload(
                    PreOpportunityDetail.product
                ),
                joinedload(PreOpportunity.details).joinedload(
                    PreOpportunityDetail.quote
                ),
                joinedload(PreOpportunity.details).joinedload(
                    PreOpportunityDetail.factory
                ),
                lazyload("*"),
            ],
        )
        if not pre_opportunity:
            raise NotFoundError(str(pre_opportunity_id))
        return pre_opportunity

    async def delete_pre_opportunity(self, pre_opportunity_id: UUID | str) -> bool:
        if not await self.repository.exists(pre_opportunity_id):
            raise NotFoundError(str(pre_opportunity_id))
        return await self.repository.delete(pre_opportunity_id)

    async def get_by_job_id(self, job_id: UUID) -> list[PreOpportunity]:
        return await self.repository.get_by_job_id(job_id)

    async def get_by_customer_id(self, customer_id: UUID) -> list[PreOpportunity]:
        return await self.repository.get_by_customer_id(customer_id)

    async def search_pre_opportunities(
        self, search_term: str, limit: int = 20
    ) -> list[PreOpportunity]:
        return await self.repository.search_by_entity_number(search_term, limit)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[PreOpportunity]:
        return await self.repository.find_by_entity(entity_type, entity_id)
