from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission import Adjustment
from commons.db.v6.commission.checks.enums.adjustment_status import AdjustmentStatus

from app.errors.common_errors import NotFoundError
from app.graphql.adjustments.repositories.adjustments_repository import (
    AdjustmentsRepository,
)
from app.graphql.adjustments.strawberry.adjustment_input import AdjustmentInput


class AdjustmentService:
    def __init__(
        self,
        repository: AdjustmentsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def find_adjustment_by_id(self, adjustment_id: UUID) -> Adjustment:
        return await self.repository.find_adjustment_by_id(adjustment_id)

    async def create_adjustment(self, adjustment_input: AdjustmentInput) -> Adjustment:
        adjustment = adjustment_input.to_orm_model()
        adjustment.locked = False
        adjustment.status = AdjustmentStatus.PENDING
        created = await self.repository.create(adjustment)
        return await self.repository.find_adjustment_by_id(created.id)

    async def update_adjustment(self, adjustment_input: AdjustmentInput) -> Adjustment:
        if adjustment_input.id is None:
            raise ValueError("ID must be provided for update")

        adjustment = adjustment_input.to_orm_model()
        adjustment.id = adjustment_input.id
        updated = await self.repository.update(adjustment)
        return await self.repository.find_adjustment_by_id(updated.id)

    async def delete_adjustment(self, adjustment_id: UUID) -> bool:
        if not await self.repository.exists(adjustment_id):
            raise NotFoundError(str(adjustment_id))
        return await self.repository.delete(adjustment_id)

    async def search_adjustments(
        self, search_term: str, limit: int = 20
    ) -> list[Adjustment]:
        return await self.repository.search_by_reason(search_term, limit)
