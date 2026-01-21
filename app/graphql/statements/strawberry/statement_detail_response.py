from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.statements import CommissionStatementDetail

from app.core.db.adapters.dto import DTOMixin
from app.graphql.invoices.strawberry.invoice_lite_response import InvoiceLiteResponse
from app.graphql.orders.strawberry.order_detail_response import OrderDetailLiteResponse
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.statements.strawberry.statement_split_rate_response import (
    StatementSplitRateResponse,
)
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse
from app.graphql.v2.core.products.strawberry.product_uom_response import (
    ProductUomResponse,
)


@strawberry.type
class StatementDetailResponse(DTOMixin[CommissionStatementDetail]):
    _instance: strawberry.Private[CommissionStatementDetail]
    id: UUID
    statement_id: UUID
    sold_to_customer_id: UUID | None
    order_id: UUID | None
    order_detail_id: UUID | None
    invoice_id: UUID | None
    item_number: int
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal
    total: Decimal
    total_line_commission: Decimal
    commission_rate: Decimal
    commission: Decimal
    commission_discount_rate: Decimal
    commission_discount: Decimal
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

    @classmethod
    def from_orm_model(cls, model: CommissionStatementDetail) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            statement_id=model.statement_id,
            sold_to_customer_id=model.sold_to_customer_id,
            order_id=model.order_id,
            order_detail_id=model.order_detail_id,
            invoice_id=model.invoice_id,
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
        )

    @strawberry.field
    def sold_to_customer(self) -> CustomerLiteResponse | None:
        return CustomerLiteResponse.from_orm_model_optional(
            self._instance.sold_to_customer
        )

    @strawberry.field
    def order(self) -> OrderLiteResponse | None:
        return OrderLiteResponse.from_orm_model_optional(self._instance.order)

    @strawberry.field
    def order_detail(self) -> OrderDetailLiteResponse | None:
        return OrderDetailLiteResponse.from_orm_model_optional(
            self._instance.order_detail
        )

    @strawberry.field
    def invoice(self) -> InvoiceLiteResponse | None:
        return InvoiceLiteResponse.from_orm_model_optional(self._instance.invoice)

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
    def outside_split_rates(self) -> list[StatementSplitRateResponse]:
        return StatementSplitRateResponse.from_orm_model_list(
            self._instance.outside_split_rates
        )
