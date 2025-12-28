import strawberry

from app.graphql.jobs.strawberry.job_response import JobLiteType
from app.graphql.orders.strawberry.order_balance_response import OrderBalanceResponse
from app.graphql.orders.strawberry.order_detail_response import OrderDetailResponse
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class OrderResponse(OrderLiteResponse):
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
    def balance(self) -> OrderBalanceResponse:
        return OrderBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[OrderDetailResponse]:
        return OrderDetailResponse.from_orm_model_list(self._instance.details)

    @strawberry.field
    def job(self) -> JobLiteType | None:
        return JobLiteType.from_orm_model_optional(self._instance.job)
