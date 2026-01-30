from datetime import date
from decimal import Decimal
from typing import Sequence
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
from commons.db.v6.crm.quotes import Quote, QuoteDetail, QuoteInsideRep, QuoteSplitRate

from app.graphql.orders.strawberry.quote_detail_to_order_input import (
    QuoteDetailToOrderDetailInput,
)


class OrderFactory:
    @staticmethod
    def _convert_to_order_split_rates(
        split_rates: Sequence[QuoteSplitRate | OrderSplitRate],
    ) -> list[OrderSplitRate]:
        result = []
        for sr in split_rates:
            obj = OrderSplitRate(user_id=sr.user_id, position=sr.position)
            obj.split_rate = sr.split_rate
            result.append(obj)
        return result

    @staticmethod
    def _convert_to_order_inside_reps(
        inside_reps: Sequence[QuoteInsideRep | OrderInsideRep],
    ) -> list[OrderInsideRep]:
        result = []
        for ir in inside_reps:
            obj = OrderInsideRep(user_id=ir.user_id, position=ir.position)
            obj.split_rate = ir.split_rate
            result.append(obj)
        return result

    @staticmethod
    def from_order(
        order: Order,
        new_order_number: str,
        new_sold_to_customer_id: UUID,
    ) -> Order:
        today = date.today()
        return Order(
            inside_per_line_item=order.inside_per_line_item,
            outside_per_line_item=order.outside_per_line_item,
            end_user_per_line_item=order.end_user_per_line_item,
            order_number=new_order_number,
            entity_date=today,
            due_date=order.due_date or today,
            factory_id=order.factory_id,
            sold_to_customer_id=new_sold_to_customer_id,
            bill_to_customer_id=order.bill_to_customer_id,
            freight_terms=order.freight_terms,
            status=OrderStatus.OPEN,
            header_status=OrderHeaderStatus.OPEN,
            order_type=order.order_type,
            creation_type=CreationType.API,
            published=False,
            job_id=order.job_id,
            details=OrderFactory._map_order_details(order.details),
        )

    @staticmethod
    def _map_order_details(order_details: list[OrderDetail]) -> list[OrderDetail]:
        result = []
        for detail in order_details:
            outside_reps = OrderFactory._convert_to_order_split_rates(
                detail.outside_split_rates
            )
            inside_reps = OrderFactory._convert_to_order_inside_reps(
                detail.inside_split_rates
            )

            new_detail = OrderDetail(
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
                freight_charge=detail.freight_charge,
                outside_split_rates=outside_reps,
                inside_split_rates=inside_reps,
            )
            new_detail.commission_rate = detail.commission_rate
            new_detail.commission = detail.commission
            new_detail.commission_discount_rate = detail.commission_discount_rate
            new_detail.commission_discount = detail.commission_discount
            new_detail.total_line_commission = detail.total_line_commission
            result.append(new_detail)
        return result

    @staticmethod
    def from_quote(
        quote: Quote,
        order_number: str,
        factory_id: UUID,
        due_date: date | None = None,
        quote_details_inputs: list[QuoteDetailToOrderDetailInput] | None = None,
    ) -> Order:
        if not quote.sold_to_customer_id:
            msg = "Cannot create order from quote without sold_to_customer_id"
            raise ValueError(msg)
        today = date.today()
        if not quote.sold_to_customer_id:
            msg = "Cannot create order from quote without a sold-to customer."
            raise ValueError(msg)
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
            published=True,
            quote_id=quote.id,
            details=OrderFactory._map_quote_details(
                quote.details, quote_details_inputs
            ),
            job_id=quote.job_id,
        )

    @staticmethod
    def _map_quote_details(
        quote_details: list[QuoteDetail],
        quote_details_inputs: list[QuoteDetailToOrderDetailInput] | None = None,
    ) -> list[OrderDetail]:
        quote_detail_map = {detail.id: detail for detail in quote_details}

        order_details: list[OrderDetail] = []
        for detail_input in quote_details_inputs or []:
            detail = quote_detail_map.get(detail_input.quote_detail_id)
            if not detail:
                continue

            outside_reps = OrderFactory._convert_to_order_split_rates(
                detail.outside_split_rates
            )
            inside_reps = OrderFactory._convert_to_order_inside_reps(
                detail.inside_split_rates
            )

            order_detail = OrderDetail(
                item_number=detail.item_number,
                quantity=detail_input.quantity or detail.quantity,
                unit_price=detail_input.unit_price or detail.unit_price,
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
                freight_charge=Decimal("0"),
                outside_split_rates=outside_reps,
                inside_split_rates=inside_reps,
            )
            order_detail.commission_rate = detail.commission_rate
            order_detail.commission = detail.commission
            order_detail.commission_discount_rate = detail.commission_discount_rate
            order_detail.commission_discount = detail.commission_discount
            order_detail.total_line_commission = detail.total_line_commission
            order_details.append(order_detail)
        return order_details
