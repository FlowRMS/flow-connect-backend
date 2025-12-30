from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import InvoiceSplitRate

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class InvoiceSplitRateResponse(DTOMixin[InvoiceSplitRate]):
    _instance: strawberry.Private[InvoiceSplitRate]
    id: UUID
    invoice_detail_id: UUID
    user_id: UUID
    split_rate: Decimal
    position: int

    @classmethod
    def from_orm_model(cls, model: InvoiceSplitRate) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            invoice_detail_id=model.invoice_detail_id,
            user_id=model.user_id,
            split_rate=model.split_rate,
            position=model.position,
        )

    @strawberry.field
    def user(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.user)
