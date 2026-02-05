from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import WarehouseMember
from commons.db.v6.warehouse.warehouse_member_role import WarehouseMemberRole

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class WarehouseMemberResponse(DTOMixin[WarehouseMember]):
    _instance: strawberry.Private[WarehouseMember]
    id: UUID
    warehouse_id: UUID
    user_id: UUID
    role: WarehouseMemberRole
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: WarehouseMember) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            user_id=model.user_id,
            role=model.role,
            created_at=model.created_at,
        )
