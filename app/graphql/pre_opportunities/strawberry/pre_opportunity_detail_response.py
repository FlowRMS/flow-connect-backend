"""GraphQL response type for PreOpportunityDetail."""

from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.models.core.product import Product
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.adapters.dto import DTOMixin
from app.graphql.inject import inject
from app.graphql.pre_opportunities.models.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)
from app.graphql.products.strawberry.product_response import ProductResponse


@strawberry.type
class PreOpportunityDetailResponse(DTOMixin[PreOpportunityDetail]):
    id: UUID
    pre_opportunity_id: UUID
    quantity: Decimal
    item_number: int
    unit_price: Decimal
    subtotal: Decimal
    discount_rate: Decimal
    discount: Decimal
    total: Decimal
    product_id: UUID
    product_cpn_id: UUID | None
    end_user_id: UUID
    lead_time: str | None

    @classmethod
    def from_orm_model(cls, model: PreOpportunityDetail) -> Self:
        return cls(
            id=model.id,
            pre_opportunity_id=model.pre_opportunity_id,
            quantity=model.quantity,
            item_number=model.item_number,
            unit_price=model.unit_price,
            subtotal=model.subtotal,
            discount_rate=model.discount_rate,
            discount=model.discount,
            total=model.total,
            product_id=model.product_id,
            product_cpn_id=model.product_cpn_id,
            end_user_id=model.end_user_id,
            lead_time=model.lead_time,
        )

    @strawberry.field
    @inject
    async def product(self, session: Injected[AsyncSession]) -> ProductResponse:
        return ProductResponse.from_orm_model(
            await session.get_one(Product, self.product_id)
        )
