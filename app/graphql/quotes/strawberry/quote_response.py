import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.jobs.strawberry.job_response import JobLiteType
from app.graphql.quotes.strawberry.quote_balance_response import QuoteBalanceResponse
from app.graphql.quotes.strawberry.quote_detail_response import QuoteDetailResponse
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class QuoteResponse(QuoteLiteResponse):
    @strawberry.field
    def url(self) -> str:
        return f"/crm/quotes/list/{self.id}"

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def sold_to_customer(self) -> CustomerLiteResponse:
        return CustomerLiteResponse.from_orm_model(self._instance.sold_to_customer)

    @strawberry.field
    def bill_to_customer(self) -> CustomerLiteResponse | None:
        if self._instance.bill_to_customer is None:
            return None
        return CustomerLiteResponse.from_orm_model(self._instance.bill_to_customer)

    @strawberry.field
    def balance(self) -> QuoteBalanceResponse:
        return QuoteBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[QuoteDetailResponse]:
        return QuoteDetailResponse.from_orm_model_list(self._instance.details)

    @strawberry.field
    def job(self) -> JobLiteType | None:
        return JobLiteType.from_orm_model_optional(self._instance.job)

    @strawberry.field
    @inject
    async def watchers(
        self,
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        users = await watcher_service.get_watchers(EntityType.QUOTE, self.id)
        return [UserResponse.from_orm_model(u) for u in users]
