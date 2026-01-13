import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.jobs.strawberry.job_response import JobLiteType
from app.graphql.orders.strawberry.order_balance_response import OrderBalanceResponse
from app.graphql.orders.strawberry.order_detail_response import OrderDetailResponse
from app.graphql.orders.strawberry.order_semi_lite_response import OrderSemiLiteResponse
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class OrderResponse(OrderSemiLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def balance(self) -> OrderBalanceResponse:
        return OrderBalanceResponse.from_orm_model(self._instance.balance)

    @strawberry.field
    def factory(self) -> FactoryLiteResponse:
        return FactoryLiteResponse.from_orm_model(self._instance.factory)

    @strawberry.field
    def details(self) -> list[OrderDetailResponse]:
        return OrderDetailResponse.from_orm_model_list(self._instance.details)

    @strawberry.field
    def job(self) -> JobLiteType | None:
        return JobLiteType.from_orm_model_optional(self._instance.job)

    @strawberry.field
    @inject
    async def watchers(
        self,
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        users = await watcher_service.get_watchers(EntityType.ORDER, self.id)
        return [UserResponse.from_orm_model(u) for u in users]
