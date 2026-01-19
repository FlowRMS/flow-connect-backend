import strawberry

from app.graphql.invoices.strawberry.invoice_balance_response import (
    InvoiceBalanceResponse,
)
from app.graphql.invoices.strawberry.invoice_detail_response import (
    InvoiceDetailResponse,
)
from app.graphql.invoices.strawberry.invoice_lite_response import InvoiceLiteResponse
from app.graphql.orders.strawberry.order_response import OrderSemiLiteResponse
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class InvoiceLiteCheckResponse(InvoiceLiteResponse):
    @strawberry.field
    def order(self) -> OrderSemiLiteResponse:
        return OrderSemiLiteResponse.from_orm_model(self._instance.order)

    @strawberry.field
    def sales_reps(self) -> list[UserResponse]:
        details = self._instance.details
        users: list[UserResponse] = []
        user_keys = set()
        for detail in details:
            osrs = detail.outside_split_rates
            for osr in osrs:
                if osr.user_id not in user_keys:
                    user_keys.add(osr.user_id)
                    users.append(UserResponse.from_orm_model(osr.user))
        return users

    @strawberry.field
    def balance(self) -> InvoiceBalanceResponse:
        return InvoiceBalanceResponse.from_orm_model(self._instance.balance)


@strawberry.type
class InvoiceResponse(InvoiceLiteResponse):
    @strawberry.field
    def order(self) -> OrderSemiLiteResponse:
        return OrderSemiLiteResponse.from_orm_model(self._instance.order)

    @strawberry.field
    def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(self._instance.factory)

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def balance(self) -> InvoiceBalanceResponse:
        return InvoiceBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[InvoiceDetailResponse]:
        return InvoiceDetailResponse.from_orm_model_list(self._instance.details)
