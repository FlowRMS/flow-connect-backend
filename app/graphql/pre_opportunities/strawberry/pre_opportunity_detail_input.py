"""GraphQL input type for creating/updating pre-opportunity details."""

from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.crm.pre_opportunities.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class PreOpportunityDetailInput(BaseInputGQL[PreOpportunityDetail]):
    """Input for creating/updating a pre-opportunity detail."""

    quantity: Decimal
    item_number: int
    unit_price: Decimal
    discount_rate: Decimal
    product_id: UUID
    end_user_id: UUID

    id: UUID | None = None
    product_cpn_id: UUID | None = None
    lead_time: str | None = None

    def to_orm_model(self) -> PreOpportunityDetail:
        quantity = self.quantity
        unit_price = self.unit_price
        subtotal = Decimal(quantity) * unit_price
        discount = subtotal * (self.discount_rate / Decimal("100"))
        total = subtotal - discount
        detail = PreOpportunityDetail(
            quantity=quantity,
            item_number=self.item_number,
            unit_price=unit_price,
            product_id=self.product_id,
            end_user_id=self.end_user_id,
            subtotal=subtotal,
            discount_rate=self.discount_rate,
            discount=discount,
            total=total,
            product_cpn_id=self.optional_field(self.product_cpn_id),
            lead_time=self.optional_field(self.lead_time),
        )
        return detail
