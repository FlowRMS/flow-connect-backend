from uuid import UUID

from commons.db.v6.crm.quotes import Quote

from app.errors.common_errors import ValidationError
from app.graphql.orders.strawberry.quote_detail_to_order_input import (
    QuoteDetailToOrderDetailInput,
)


def validate_quote_details_same_factory(
    quote: Quote,
    quote_details_inputs: list[QuoteDetailToOrderDetailInput] | None,
) -> None:
    """
    Validates that all selected quote details have the same factory_id.

    When factory_per_line_item is enabled on a quote, each line item can have
    a different manufacturer. However, an Order can only have one factory_id
    at the header level. This validation ensures users cannot accidentally
    create orders with line items from multiple manufacturers.
    """
    if not quote_details_inputs:
        return

    quote_detail_map = {detail.id: detail for detail in quote.details}

    factory_ids: set[UUID | None] = set()
    for detail_input in quote_details_inputs:
        quote_detail = quote_detail_map.get(detail_input.quote_detail_id)
        if quote_detail:
            factory_ids.add(quote_detail.factory_id)

    non_null_factory_ids = {fid for fid in factory_ids if fid is not None}

    if len(non_null_factory_ids) > 1:
        raise ValidationError(
            "Cannot create order from line items with different manufacturers. "
            "All selected quote line items must have the same factory. "
            "Please select line items from only one manufacturer."
        )
