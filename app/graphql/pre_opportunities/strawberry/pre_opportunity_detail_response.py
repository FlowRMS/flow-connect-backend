"""GraphQL response type for PreOpportunityDetail."""

from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.pre_opportunities.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)

from app.core.db.adapters.dto import DTOMixin
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


@strawberry.type
class PreOpportunityDetailResponse(DTOMixin[PreOpportunityDetail]):
    _instance: strawberry.Private[PreOpportunityDetail]
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
            _instance=model,
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
    def product(self) -> ProductLiteResponse:
        return ProductLiteResponse.from_orm_model(self._instance.product)

    @strawberry.field
    def quote(self) -> QuoteLiteResponse | None:
        return QuoteLiteResponse.from_orm_model_optional(self._instance.quote)
