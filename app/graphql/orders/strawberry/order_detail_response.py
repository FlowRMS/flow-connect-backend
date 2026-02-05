from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderDetail, OrderStatus

from app.core.db.adapters.dto import DTOMixin
from app.graphql.invoices.strawberry.invoice_lite_response import InvoiceLiteResponse
from app.graphql.orders.strawberry.order_inside_rep_response import (
    OrderInsideRepResponse,
)
from app.graphql.orders.strawberry.order_split_rate_response import (
    OrderSplitRateResponse,
)
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse
from app.graphql.v2.core.products.strawberry.product_uom_response import (
    ProductUomResponse,
)


@strawberry.type
class OrderDetailLiteResponse(DTOMixin[OrderDetail]):
    _instance: strawberry.Private[OrderDetail]
    id: UUID
    order_id: UUID
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
    product_id: UUID | None
    product_name_adhoc: str | None
    product_description_adhoc: str | None
    end_user_id: UUID | None
    lead_time: str | None
    note: str | None
    status: OrderStatus
    division_factor: Decimal | None
    freight_charge: Decimal
    shipping_balance: Decimal
    cancelled_balance: Decimal

    @classmethod
    def from_orm_model(cls, model: OrderDetail) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            order_id=model.order_id,
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
            product_id=model.product_id,
            product_name_adhoc=model.product_name_adhoc,
            product_description_adhoc=model.product_description_adhoc,
            end_user_id=model.end_user_id,
            lead_time=model.lead_time,
            note=model.note,
            status=model.status,
            division_factor=model.division_factor,
            freight_charge=model.freight_charge,
            shipping_balance=model.shipping_balance,
            cancelled_balance=model.cancelled_balance,
        )


@strawberry.type
class OrderDetailResponse(OrderDetailLiteResponse):
    @strawberry.field
    def outside_split_rates(self) -> list[OrderSplitRateResponse]:
        return OrderSplitRateResponse.from_orm_model_list(
            self._instance.outside_split_rates
        )

    @strawberry.field
    def end_user(self) -> CustomerLiteResponse | None:
        return CustomerLiteResponse.from_orm_model_optional(self._instance.end_user)

    @strawberry.field
    def inside_split_rates(self) -> list[OrderInsideRepResponse]:
        return OrderInsideRepResponse.from_orm_model_list(
            self._instance.inside_split_rates
        )

    @strawberry.field
    def product(self) -> ProductLiteResponse | None:
        return ProductLiteResponse.from_orm_model_optional(self._instance.product)

    @strawberry.field
    def uom(self) -> ProductUomResponse | None:
        return ProductUomResponse.from_orm_model_optional(self._instance.uom)

    @strawberry.field(deprecation_reason="Use 'invoices' field instead")
    def invoice(self) -> InvoiceLiteResponse | None:
        invoices = self._instance.invoices
        if not invoices:
            return None
        return InvoiceLiteResponse.from_orm_model(invoices[0])

    @strawberry.field
    def invoices(self) -> list[InvoiceLiteResponse] | None:
        return InvoiceLiteResponse.from_orm_model_list(self._instance.invoices)
