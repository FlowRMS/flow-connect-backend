from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import InvoiceDetail

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.invoices.strawberry.invoice_split_rate_input import (
    InvoiceSplitRateInput,
)


@strawberry.input
class InvoiceDetailInput(BaseInputGQL[InvoiceDetail]):
    item_number: int
    quantity: Decimal
    unit_price: Decimal
    id: UUID | None = None
    order_detail_id: UUID | None = None
    uom_id: UUID | None = None
    division_factor: Decimal | None = None
    product_id: UUID | None = None
    product_name_adhoc: str | None = None
    product_description_adhoc: str | None = None
    end_user_id: UUID | None = None
    lead_time: str | None = None
    note: str | None = None
    discount_rate: Decimal = Decimal("0")
    commission_rate: Decimal = Decimal("0")
    commission: Decimal | None = (
        None  # If provided, commission_rate is calculated from it
    )
    commission_discount_rate: Decimal = Decimal("0")
    outside_split_rates: list[InvoiceSplitRateInput] | None = None

    def to_orm_model(self) -> InvoiceDetail:
        quantity = self.quantity if self.quantity is not None else Decimal("0")
        unit_price = self.unit_price if self.unit_price is not None else Decimal("0")

        subtotal = quantity * unit_price
        discount = subtotal * (self.discount_rate / Decimal("100"))
        total = subtotal - discount

        # If commission value is provided, calculate commission_rate from it
        # Formula: commission_rate = (commission / total) * 100
        if self.commission is not None:
            commission = self.commission
            commission_rate = (
                (commission / total * Decimal("100")) if total != 0 else Decimal("0")
            )
        else:
            commission_rate = self.commission_rate
            commission = total * (commission_rate / Decimal("100"))

        commission_discount = commission * (
            self.commission_discount_rate / Decimal("100")
        )
        total_line_commission = commission - commission_discount

        detail = InvoiceDetail(
            item_number=self.item_number,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
            discount_rate=self.discount_rate,
            discount=discount,
            total=total,
            commission_rate=commission_rate,
            commission=commission,
            commission_discount_rate=self.commission_discount_rate,
            commission_discount=commission_discount,
            total_line_commission=total_line_commission,
            product_id=self.product_id,
            product_name_adhoc=self.product_name_adhoc,
            product_description_adhoc=self.product_description_adhoc,
            end_user_id=self.end_user_id,
            uom_id=self.uom_id,
            division_factor=self.division_factor,
            lead_time=self.lead_time,
            note=self.note,
            outside_split_rates=(
                [sr.to_orm_model() for sr in self.outside_split_rates]
                if self.outside_split_rates
                else []
            ),
        )
        if self.order_detail_id:
            detail.order_detail_id = self.order_detail_id
        detail.invoiced_balance = total
        if self.id:
            detail.id = self.id
        return detail
