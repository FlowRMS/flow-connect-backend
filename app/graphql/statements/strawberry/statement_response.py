import strawberry

from app.graphql.statements.strawberry.statement_balance_response import (
    StatementBalanceResponse,
)
from app.graphql.statements.strawberry.statement_detail_response import (
    StatementDetailResponse,
)
from app.graphql.statements.strawberry.statement_lite_response import (
    StatementLiteResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class StatementResponse(StatementLiteResponse):
    @strawberry.field
    def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(self._instance.factory)

    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def balance(self) -> StatementBalanceResponse:
        return StatementBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def details(self) -> list[StatementDetailResponse]:
        return StatementDetailResponse.from_orm_model_list(self._instance.details)
