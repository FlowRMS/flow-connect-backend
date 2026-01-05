from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission.orders import OrderAcknowledgement

from app.errors.common_errors import NotFoundError
from app.graphql.orders.repositories.order_acknowledgement_repository import (
    OrderAcknowledgementRepository,
)
from app.graphql.orders.strawberry.order_acknowledgement_input import (
    OrderAcknowledgementInput,
)


class OrderAcknowledgementService:
    def __init__(
        self,
        repository: OrderAcknowledgementRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, acknowledgement_id: UUID) -> OrderAcknowledgement | None:
        return await self.repository.get_by_id(acknowledgement_id)

    async def find_by_order_id(self, order_id: UUID) -> list[OrderAcknowledgement]:
        return await self.repository.find_by_order_id(order_id)

    async def find_by_order_detail_id(
        self, order_detail_id: UUID
    ) -> list[OrderAcknowledgement]:
        return await self.repository.find_by_order_detail_id(order_detail_id)

    async def create(self, input: OrderAcknowledgementInput) -> OrderAcknowledgement:
        acknowledgement = input.to_orm_model()
        return await self.repository.create(acknowledgement)

    async def update(self, input: OrderAcknowledgementInput) -> OrderAcknowledgement:
        if input.id is None:
            raise ValueError("ID must be provided for update")

        acknowledgement = input.to_orm_model()
        acknowledgement.id = input.id
        return await self.repository.update(acknowledgement)

    async def delete(self, acknowledgement_id: UUID) -> bool:
        if not await self.repository.exists(acknowledgement_id):
            raise NotFoundError(str(acknowledgement_id))
        return await self.repository.delete(acknowledgement_id)
