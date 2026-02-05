from uuid import UUID

import strawberry
from commons.db.v6 import WarehouseMember
from commons.db.v6.warehouse.warehouse_member_role import WarehouseMemberRole

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class WarehouseMemberInput(BaseInputGQL[WarehouseMember]):
    warehouse_id: UUID
    user_id: UUID
    role: WarehouseMemberRole

    def to_orm_model(self) -> WarehouseMember:
        return WarehouseMember(
            warehouse_id=self.warehouse_id,
            user_id=self.user_id,
            role=self.role,
        )
