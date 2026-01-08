from typing import override
from uuid import UUID

from app.graphql.common.entity_source_type import EntitySourceType
from app.graphql.common.interfaces.entity_lookup_strategy import EntityLookupStrategy
from app.graphql.common.strawberry.entity_response import EntityResponse
from app.graphql.orders.services.order_service import OrderService
from app.graphql.orders.strawberry.order_response import OrderResponse


class OrderEntityStrategy(EntityLookupStrategy):
    def __init__(self, service: OrderService) -> None:
        super().__init__()
        self.service = service

    @override
    def get_supported_source_type(self) -> EntitySourceType:
        return EntitySourceType.ORDERS

    @override
    async def get_entity(self, entity_id: UUID) -> EntityResponse:
        order = await self.service.find_order_by_id(entity_id)
        return OrderResponse.from_orm_model(order)
