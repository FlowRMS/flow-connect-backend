import strawberry

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
