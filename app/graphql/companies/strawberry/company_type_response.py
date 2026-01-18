from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.companies import CompanyTypeEntity

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class CompanyTypeResponse(DTOMixin[CompanyTypeEntity]):
    id: UUID
    name: str
    display_order: int
    is_active: bool
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: CompanyTypeEntity) -> Self:
        return cls(
            id=model.id,
            name=model.name,
            display_order=model.display_order,
            is_active=model.is_active,
            created_at=model.created_at,
        )
