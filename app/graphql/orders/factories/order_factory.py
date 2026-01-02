from datetime import date
from decimal import Decimal
from uuid import UUID

from commons.db.v6.commission.orders import (
    Order,
    OrderDetail,
    OrderHeaderStatus,
    OrderInsideRep,
    OrderSplitRate,
    OrderStatus,
    OrderType,
)
from commons.db.v6.common.creation_type import CreationType
from commons.db.v6.crm.quotes import Quote, QuoteDetail


class OrderFactory:
    @staticmethod
    def from_quote(
        quote: Quote,
        order_number: str,
        factory_id: UUID,
        due_date: date | None = None,
        quote_detail_ids: list[UUID] | None = None,
    ) -> Order:
        today = date.today()
        details_to_map = quote.details
        if quote_detail_ids:
            detail_ids_set = set(quote_detail_ids)
            details_to_map = [d for d in quote.details if d.id in detail_ids_set]

        return Order(
            inside_per_line_item=quote.inside_per_line_item,
            outside_per_line_item=quote.outside_per_line_item,
            end_user_per_line_item=quote.end_user_per_line_item,
            order_number=order_number,
            entity_date=today,
            due_date=due_date or today,
            factory_id=factory_id,
            sold_to_customer_id=quote.sold_to_customer_id,
            bill_to_customer_id=quote.bill_to_customer_id,
            freight_terms=quote.freight_terms,
            status=OrderStatus.OPEN,
            header_status=OrderHeaderStatus.OPEN,
            order_type=OrderType.NORMAL,
            creation_type=CreationType.API,
            published=False,
            quote_id=quote.id,
            details=OrderFactory._map_quote_details(details_to_map),
        )

    @staticmethod
    def _map_quote_details(quote_details: list[QuoteDetail]) -> list[OrderDetail]:
        return [
            OrderDetail(
                item_number=detail.item_number,
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                subtotal=detail.subtotal,
                discount_rate=detail.discount_rate,
                discount=detail.discount,
                total=detail.total,
                product_id=detail.product_id,
                product_name_adhoc=detail.product_name_adhoc,
                product_description_adhoc=detail.product_description_adhoc,
                uom_id=detail.uom_id,
                end_user_id=detail.end_user_id,
                lead_time=detail.lead_time,
                note=detail.note,
                commission_rate=detail.commission_rate,
                commission=detail.commission,
                commission_discount_rate=detail.commission_discount_rate,
                commission_discount=detail.commission_discount,
                total_line_commission=detail.total_line_commission,
                freight_charge=Decimal("0"),
                outside_split_rates=[
                    OrderSplitRate(
                        user_id=sr.user_id,
                        split_rate=sr.split_rate,
                        position=sr.position,
                    )
                    for sr in detail.outside_split_rates
                ],
                inside_split_rates=[
                    OrderInsideRep(
                        user_id=ir.user_id,
                        split_rate=ir.split_rate,
                        position=ir.position,
                    )
                    for ir in detail.inside_split_rates
                ],
            )
            for detail in quote_details
        ]
