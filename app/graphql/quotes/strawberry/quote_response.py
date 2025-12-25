import strawberry

from app.graphql.quotes.strawberry.quote_balance_response import QuoteBalanceResponse
from app.graphql.quotes.strawberry.quote_detail_response import QuoteDetailResponse
from app.graphql.quotes.strawberry.quote_inside_rep_response import (
    QuoteInsideRepResponse,
)
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class QuoteResponse(QuoteLiteResponse):
    @strawberry.field
    def url(self) -> str:
        return f"/crm/quotes/list/{self.id}"

    @strawberry.field
    async def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(
            await self._instance.awaitable_attrs.created_by
        )

    @strawberry.field
    async def sold_to_customer(self) -> CustomerLiteResponse:
        return CustomerLiteResponse.from_orm_model(
            await self._instance.awaitable_attrs.sold_to_customer
        )

    @strawberry.field
    async def bill_to_customer(self) -> CustomerLiteResponse | None:
        if self._instance.bill_to_customer_id is None:
            return None
        return CustomerLiteResponse.from_orm_model(
            await self._instance.awaitable_attrs.bill_to_customer
        )

    @strawberry.field
    def balance(self) -> QuoteBalanceResponse:
        return QuoteBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[QuoteDetailResponse]:
        return QuoteDetailResponse.from_orm_model_list(self._instance.details)

    @strawberry.field
    def inside_reps(self) -> list[QuoteInsideRepResponse]:
        return QuoteInsideRepResponse.from_orm_model_list(self._instance.inside_reps)
