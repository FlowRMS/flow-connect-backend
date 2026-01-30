from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.crm.quotes import QuoteDetail, QuoteDetailStatus

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.quotes.strawberry.quote_inside_rep_input import QuoteInsideRepInput
from app.graphql.quotes.strawberry.quote_split_rate_input import QuoteSplitRateInput


@strawberry.input
class QuoteDetailInput(BaseInputGQL[QuoteDetail]):
    item_number: int
    quantity: Decimal
    unit_price: Decimal

    id: UUID | None = None
    uom_id: UUID | None = None
    division_factor: Decimal | None = None
    product_id: UUID | None = None
    product_name_adhoc: str | None = None
    product_description_adhoc: str | None = None
    factory_id: UUID | None = None
    end_user_id: UUID | None = None
    lead_time: str | None = None
    note: str | None = None
    status: QuoteDetailStatus = QuoteDetailStatus.OPEN
    discount_rate: Decimal = Decimal("0")
    commission_rate: Decimal = Decimal("0")
    commission_discount_rate: Decimal = Decimal("0")
    outside_split_rates: list[QuoteSplitRateInput] | None = None
    inside_split_rates: list[QuoteInsideRepInput] | None = None
    # Overage fields
    overage_commission_rate: Decimal | None = None
    overage_commission: Decimal | None = None
    overage_unit_price: Decimal | None = None
    # Fixture schedule
    fixture_schedule: str | None = None

    def to_orm_model(self) -> QuoteDetail:
        quantity = self.quantity if self.quantity is not None else Decimal("0")
        unit_price = self.unit_price if self.unit_price is not None else Decimal("0")

        subtotal = quantity * unit_price
        discount = subtotal * (self.discount_rate / Decimal("100"))
        total = subtotal - discount
        commission = total * (self.commission_rate / Decimal("100"))
        commission_discount = commission * (
            self.commission_discount_rate / Decimal("100")
        )
        total_line_commission = commission - commission_discount

        detail = QuoteDetail(
            item_number=self.item_number,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
            discount_rate=self.discount_rate,
            discount=discount,
            total=total,
            product_id=self.product_id,
            product_name_adhoc=self.product_name_adhoc,
            product_description_adhoc=self.product_description_adhoc,
            factory_id=self.factory_id,
            end_user_id=self.end_user_id,
            uom_id=self.uom_id,
            division_factor=self.division_factor,
            lead_time=self.lead_time,
            note=self.note,
            status=self.status,
            outside_split_rates=(
                [sr.to_orm_model() for sr in self.outside_split_rates]
                if self.outside_split_rates
                else []
            ),
            inside_split_rates=(
                [ir.to_orm_model() for ir in self.inside_split_rates]
                if self.inside_split_rates
                else []
            ),
            overage_commission_rate=self.overage_commission_rate,
            overage_commission=self.overage_commission,
            overage_unit_price=self.overage_unit_price,
            fixture_schedule=self.fixture_schedule,
        )
        detail.commission_rate = self.commission_rate
        detail.commission = commission
        detail.commission_discount_rate = self.commission_discount_rate
        detail.commission_discount = commission_discount
        detail.total_line_commission = total_line_commission
        if self.id:
            detail.id = self.id
        return detail
