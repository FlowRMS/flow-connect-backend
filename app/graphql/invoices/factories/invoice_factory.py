from datetime import date
from uuid import UUID

from commons.db.v6.commission import Invoice, InvoiceDetail, InvoiceSplitRate
from commons.db.v6.commission.orders import Order, OrderDetail
from commons.db.v6.common.creation_type import CreationType


class InvoiceFactory:
    @staticmethod
    def from_order(
        order: Order,
        invoice_number: str,
        factory_id: UUID,
        order_detail_ids: list[UUID] | None = None,
        due_date: date | None = None,
    ) -> Invoice:
        details_to_use = order.details
        if order_detail_ids:
            details_to_use = [d for d in order.details if d.id in order_detail_ids]

        return Invoice(
            invoice_number=invoice_number,
            entity_date=date.today(),
            due_date=due_date,
            factory_id=factory_id,
            order_id=order.id,
            creation_type=CreationType.API,
            published=False,
            locked=False,
            details=InvoiceFactory._map_order_details(details_to_use),
        )

    @staticmethod
    def _map_order_details(order_details: list[OrderDetail]) -> list[InvoiceDetail]:
        invoice_details: list[InvoiceDetail] = []
        for detail in order_details:
            invoice_detail = InvoiceDetail(
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
