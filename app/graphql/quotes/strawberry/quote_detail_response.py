from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.quotes import QuoteDetail, QuoteDetailStatus

from app.core.db.adapters.dto import DTOMixin
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.quotes.strawberry.quote_inside_rep_response import (
    QuoteInsideRepResponse,
)
from app.graphql.quotes.strawberry.quote_split_rate_response import (
    QuoteSplitRateResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse
from app.graphql.v2.core.products.strawberry.product_uom_response import (
    ProductUomResponse,
)


@strawberry.type
class QuoteDetailResponse(DTOMixin[QuoteDetail]):
    _instance: strawberry.Private[QuoteDetail]
    id: UUID
    quote_id: UUID
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
    factory_id: UUID | None
    end_user_id: UUID | None
    lead_time: str | None
    note: str | None
    status: QuoteDetailStatus

    @classmethod
    def from_orm_model(cls, model: QuoteDetail) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            quote_id=model.quote_id,
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
            factory_id=model.factory_id,
            end_user_id=model.end_user_id,
            lead_time=model.lead_time,
            note=model.note,
            status=model.status,
        )

    @strawberry.field
    def outside_split_rates(self) -> list[QuoteSplitRateResponse]:
        return QuoteSplitRateResponse.from_orm_model_list(
            self._instance.outside_split_rates
        )

    @strawberry.field
    def inside_split_rates(self) -> list[QuoteInsideRepResponse]:
        return QuoteInsideRepResponse.from_orm_model_list(
            self._instance.inside_split_rates
        )

    @strawberry.field
    def product(self) -> ProductLiteResponse | None:
        return ProductLiteResponse.from_orm_model_optional(self._instance.product)

    @strawberry.field
    def uom(self) -> ProductUomResponse | None:
        return ProductUomResponse.from_orm_model_optional(self._instance.uom)

    @strawberry.field
    def order(self) -> OrderLiteResponse | None:
        return OrderLiteResponse.from_orm_model_optional(self._instance.order)
