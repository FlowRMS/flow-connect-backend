import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.jobs.strawberry.job_response import JobLiteType
from app.graphql.pre_opportunities.strawberry.pre_opportunity_balance_response import (
    PreOpportunityBalanceResponse,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_detail_response import (
    PreOpportunityDetailResponse,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class PreOpportunityResponse(PreOpportunityLiteResponse):
    @strawberry.field
    def balance(self) -> PreOpportunityBalanceResponse:
        return PreOpportunityBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[PreOpportunityDetailResponse]:
        return PreOpportunityDetailResponse.from_orm_model_list(self._instance.details)

    @strawberry.field
    def job(self) -> JobLiteType | None:
        return JobLiteType.from_orm_model_optional(self._instance.job)

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    @inject
    async def watchers(
        self,
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        users = await watcher_service.get_watchers(EntityType.PRE_OPPORTUNITY, self.id)
        return [UserResponse.from_orm_model(u) for u in users]
