from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission import InvoiceDetail
from commons.db.v6.commission.invoices.invoice import InvoiceStatus

from app.core.db.adapters.dto import DTOMixin
from app.graphql.invoices.strawberry.invoice_split_rate_response import (
    InvoiceSplitRateResponse,
)
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse
from app.graphql.v2.core.products.strawberry.product_uom_response import (
    ProductUomResponse,
)


@strawberry.type
class InvoiceDetailResponse(DTOMixin[InvoiceDetail]):
    _instance: strawberry.Private[InvoiceDetail]
    id: UUID
    invoice_id: UUID
    order_detail_id: UUID | None
    item_number: int
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    total: Decimal
    total_line_commission: Decimal | None
    commission_rate: Decimal | None
    commission: Decimal | None
    commission_discount_rate: Decimal | None
    commission_discount: Decimal | None
    discount_rate: Decimal
    discount: Decimal
    division_factor: Decimal | None
    product_id: UUID | None
    product_name_adhoc: str | None
    product_description_adhoc: str | None
    uom_id: UUID | None
    end_user_id: UUID | None
    lead_time: str | None
    note: str | None
    status: InvoiceStatus
    invoiced_balance: Decimal

    @classmethod
    def from_orm_model(cls, model: InvoiceDetail) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            invoice_id=model.invoice_id,
            order_detail_id=model.order_detail_id,
            item_number=model.item_number,
            quantity=model.quantity,
            unit_price=model.unit_price,
            subtotal=model.subtotal,
            total=model.total,
            total_line_commission=model.total_line_commission,
            commission_rate=model.commission_rate,
            commission=model.commission,
            commission_discount_rate=model.commission_discount_rate,
            commission_discount=model.commission_discount,
            discount_rate=model.discount_rate,
            discount=model.discount,
            division_factor=model.division_factor,
            product_id=model.product_id,
            product_name_adhoc=model.product_name_adhoc,
            product_description_adhoc=model.product_description_adhoc,
            uom_id=model.uom_id,
            end_user_id=model.end_user_id,
            lead_time=model.lead_time,
            note=model.note,
            status=model.status,
            invoiced_balance=model.invoiced_balance,
        )

    @strawberry.field
    def end_user(self) -> CustomerLiteResponse | None:
        return CustomerLiteResponse.from_orm_model_optional(self._instance.end_user)

    @strawberry.field
    def product(self) -> ProductLiteResponse | None:
        return ProductLiteResponse.from_orm_model_optional(self._instance.product)

    @strawberry.field
    def uom(self) -> ProductUomResponse | None:
        return ProductUomResponse.from_orm_model_optional(self._instance.uom)

    @strawberry.field
    def outside_split_rates(self) -> list[InvoiceSplitRateResponse]:
        return InvoiceSplitRateResponse.from_orm_model_list(
            self._instance.outside_split_rates
        )
