import strawberry

from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)


@strawberry.type
class OrderSemiLiteResponse(OrderLiteResponse):
    @strawberry.field
    def sold_to_customer(self) -> CustomerLiteResponse:
        return CustomerLiteResponse.from_orm_model(self._instance.sold_to_customer)

    @strawberry.field
    def bill_to_customer(self) -> CustomerLiteResponse | None:
        return CustomerLiteResponse.from_orm_model_optional(
            self._instance.bill_to_customer
        )
