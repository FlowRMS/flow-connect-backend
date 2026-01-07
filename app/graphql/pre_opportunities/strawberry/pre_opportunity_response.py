"""GraphQL response type for PreOpportunity."""

# from aioinject import Injected
import strawberry

# from app.graphql.inject import inject
# from commons.db.v6.crm.jobs.jobs_model import Job
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

# from sqlalchemy.ext.asyncio import AsyncSession


@strawberry.type
class PreOpportunityResponse(PreOpportunityLiteResponse):
    @strawberry.field
    def balance(self) -> PreOpportunityBalanceResponse:
        return PreOpportunityBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[PreOpportunityDetailResponse]:
        return PreOpportunityDetailResponse.from_orm_model_list(self._instance.details)

    # @strawberry.field
    # @inject
    # async def job(self, session: Injected[AsyncSession]) -> JobType | None:
    #     if not self._instance.job:
    #         return None

    #     return JobType.from_orm_model(await session.get_one(Job, self._instance.job.id))

    @strawberry.field
    def job(self) -> JobLiteType | None:
        return JobLiteType.from_orm_model_optional(self._instance.job)

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)
