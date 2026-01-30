from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload, lazyload

from commons.db.v6.crm.quotes import Quote, QuoteDetail

QUOTE_WITH_DETAILS_OPTIONS = [
    lazyload("*"),
    joinedload(Quote.details),
    joinedload(Quote.details).joinedload(QuoteDetail.product),
    joinedload(Quote.details).joinedload(QuoteDetail.outside_split_rates),
    joinedload(Quote.details).joinedload(QuoteDetail.inside_split_rates),
    joinedload(Quote.details).joinedload(QuoteDetail.uom),
    joinedload(Quote.details).joinedload(QuoteDetail.order),
    joinedload(Quote.details).joinedload(QuoteDetail.factory),
    joinedload(Quote.details).joinedload(QuoteDetail.end_user),
    joinedload(Quote.balance),
]


def build_find_quote_by_number_with_details_stmt(
    quote_number: str,
) -> Select[Any]:
    return (
        select(Quote)
        .options(*QUOTE_WITH_DETAILS_OPTIONS)
        .where(Quote.quote_number == quote_number)
    )


def build_find_quotes_by_quote_numbers_stmt(
    quote_numbers: list[str],
) -> Select[Any]:
    if not quote_numbers:
        return select(Quote).where(Quote.id.is_(None))

    return (
        select(Quote)
        .options(*QUOTE_WITH_DETAILS_OPTIONS)
        .where(Quote.quote_number.in_(quote_numbers))
    )
