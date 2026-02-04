from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.orders.services.order_service import OrderService
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class OrderWatcherMutations:
    @strawberry.mutation
    @inject
    async def add_order_watcher(
        self,
        order_id: UUID,
        user_id: UUID,
        order_service: Injected[OrderService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await order_service.find_order_by_id(order_id)
        users = await watcher_service.add_watcher(EntityType.ORDER, order_id, user_id)
        return [UserResponse.from_orm_model(u) for u in users]

    @strawberry.mutation
    @inject
    async def remove_order_watcher(
        self,
        order_id: UUID,
        user_id: UUID,
        order_service: Injected[OrderService],
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        _ = await order_service.find_order_by_id(order_id)
        users = await watcher_service.remove_watcher(
            EntityType.ORDER, order_id, user_id
        )
        return [UserResponse.from_orm_model(u) for u in users]
