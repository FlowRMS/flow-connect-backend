from datetime import date
from uuid import UUID

from commons.db.v6.commission import Invoice, InvoiceDetail, InvoiceSplitRate
from commons.db.v6.commission.orders import Order, OrderDetail
from commons.db.v6.common.creation_type import CreationType

from app.graphql.invoices.strawberry.order_detail_to_invoice_input import (
    OrderDetailToInvoiceDetailInput,
)


class InvoiceFactory:
    @staticmethod
    def from_order(
        order: Order,
        invoice_number: str,
        factory_id: UUID,
        order_details_inputs: list[OrderDetailToInvoiceDetailInput] | None = None,
        due_date: date | None = None,
    ) -> Invoice:
        details_to_use = order.details
        return Invoice(
            invoice_number=invoice_number,
            entity_date=date.today(),
            due_date=due_date,
            factory_id=factory_id,
            order_id=order.id,
            creation_type=CreationType.API,
            published=False,
            locked=False,
            details=InvoiceFactory._map_order_details(
                details_to_use, order_details_inputs
            ),
        )

    @staticmethod
    def _map_order_details(
        order_details: list[OrderDetail],
        order_details_inputs: list[OrderDetailToInvoiceDetailInput] | None = None,
    ) -> list[InvoiceDetail]:
        order_detail_map = {detail.id: detail for detail in order_details}

        invoice_details: list[InvoiceDetail] = []
        for detail_input in order_details_inputs or []:
            detail = order_detail_map.get(detail_input.order_detail_id)
            if not detail:
                continue
            invoice_detail = InvoiceDetail(
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
                commission_rate=detail.commission_rate,
                commission=detail.commission,
                commission_discount_rate=detail.commission_discount_rate,
                commission_discount=detail.commission_discount,
                total_line_commission=detail.total_line_commission,
                outside_split_rates=[
                    InvoiceSplitRate(
                        user_id=sr.user_id,
                        split_rate=sr.split_rate,
                        position=sr.position,
                    )
                    for sr in detail.outside_split_rates
                ],
            )
            invoice_detail.order_detail_id = detail.id
            invoice_detail.invoiced_balance = detail.total
            invoice_details.append(invoice_detail)
        return invoice_details
