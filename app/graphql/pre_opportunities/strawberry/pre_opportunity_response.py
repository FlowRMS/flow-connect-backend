"""GraphQL response type for PreOpportunity."""

import strawberry

from app.graphql.pre_opportunities.strawberry.pre_opportunity_balance_response import (
    PreOpportunityBalanceResponse,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_detail_response import (
    PreOpportunityDetailResponse,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)


@strawberry.type
class PreOpportunityResponse(PreOpportunityLiteResponse):
    @strawberry.field
    def balance(self) -> PreOpportunityBalanceResponse:
        return PreOpportunityBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[PreOpportunityDetailResponse]:
        return PreOpportunityDetailResponse.from_orm_model_list(self._instance.details)
