import strawberry

from app.graphql.quotes.strawberry.quote_balance_response import QuoteBalanceResponse
from app.graphql.quotes.strawberry.quote_detail_response import QuoteDetailResponse
from app.graphql.quotes.strawberry.quote_inside_rep_response import (
    QuoteInsideRepResponse,
)
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse


@strawberry.type
class QuoteFullResponse(QuoteLiteResponse):
    @strawberry.field
    def balance(self) -> QuoteBalanceResponse:
        return QuoteBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[QuoteDetailResponse]:
        return QuoteDetailResponse.from_orm_model_list(self._instance.details)

    @strawberry.field
    def inside_reps(self) -> list[QuoteInsideRepResponse]:
        return QuoteInsideRepResponse.from_orm_model_list(self._instance.inside_reps)
