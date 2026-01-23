from datetime import date
from uuid import UUID

from commons.db.v6.commission.orders import Order, OrderDetail
from commons.db.v6.common.creation_type import CreationType

from app.graphql.invoices.strawberry.invoice_detail_input import InvoiceDetailInput
from app.graphql.invoices.strawberry.invoice_input import InvoiceInput
from app.graphql.invoices.strawberry.invoice_split_rate_input import (
    InvoiceSplitRateInput,
)
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
    ) -> InvoiceInput:
        return InvoiceInput(
            invoice_number=invoice_number,
            entity_date=date.today(),
            due_date=due_date,
            factory_id=factory_id,
            order_id=order.id,
            creation_type=CreationType.API,
            details=InvoiceFactory._map_order_details(
                order.details, order_details_inputs
            ),
        )

    @staticmethod
    def _map_order_details(
        order_details: list[OrderDetail],
        order_details_inputs: list[OrderDetailToInvoiceDetailInput] | None = None,
    ) -> list[InvoiceDetailInput]:
        order_detail_map = {detail.id: detail for detail in order_details}

        invoice_details: list[InvoiceDetailInput] = []
        for detail_input in order_details_inputs or []:
            detail = order_detail_map.get(detail_input.order_detail_id)
            if not detail:
                continue
            invoice_details.append(
                InvoiceDetailInput(
                    item_number=detail.item_number,
                    quantity=detail_input.quantity or detail.quantity,
                    unit_price=detail_input.unit_price or detail.unit_price,
                    order_detail_id=detail.id,
                    product_id=detail.product_id,
                    product_name_adhoc=detail.product_name_adhoc,
                    product_description_adhoc=detail.product_description_adhoc,
                    uom_id=detail.uom_id,
                    end_user_id=detail.end_user_id,
                    lead_time=detail.lead_time,
                    note=detail.note,
                    discount_rate=detail.discount_rate,
                    commission_rate=detail.commission_rate,
                    commission_discount_rate=detail.commission_discount_rate,
                    outside_split_rates=[
                        InvoiceSplitRateInput(
                            user_id=sr.user_id,
                            split_rate=sr.split_rate,
                            position=sr.position,
                        )
                        for sr in detail.outside_split_rates
                    ],
                )
            )
        return invoice_details
