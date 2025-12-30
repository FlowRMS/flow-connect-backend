from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.quotes import QuoteSplitRate

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class QuoteSplitRateResponse(DTOMixin[QuoteSplitRate]):
    _instance: strawberry.Private[QuoteSplitRate]
    id: UUID
    created_at: datetime
    quote_detail_id: UUID
    user_id: UUID
    split_rate: Decimal
    position: int

    @classmethod
    def from_orm_model(cls, model: QuoteSplitRate) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            quote_detail_id=model.quote_detail_id,
            user_id=model.user_id,
            split_rate=model.split_rate,
            position=model.position,
        )
