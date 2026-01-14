import decimal
from collections.abc import Sequence
from decimal import ROUND_DOWN, Decimal
from typing import Any, TypeVar

from commons.db.v6.common.base_detail import BaseDetail
from commons.db.v6.common.base_split_rate import BaseSplitRate

from app.errors.common_errors import ValidationError

T = TypeVar("T", bound=BaseDetail)


def distribute_split_rates(count: int) -> list[Decimal]:
    """
    Distribute 100% evenly among `count` items, ensuring the total sums exactly to 100.

    For cases like 3 reps: returns [33.34, 33.33, 33.33] instead of [33.33, 33.33, 33.33].
    The first item receives any remainder from rounding.
    """
    if count <= 0:
        return []

    if count == 1:
        return [Decimal("100.00")]

    base_rate = (Decimal("100") / Decimal(count)).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    total_base = base_rate * count
    remainder = Decimal("100") - total_base

    rates = [base_rate] * count
    rates[0] = rates[0] + remainder

    return rates


def validate_split_rates_sum_to_100(
    rates: Sequence[BaseSplitRate],
    *,
    label: str = "split rates",
    get_rate: Any = None,
) -> None:
    from app.errors.common_errors import ValidationError

    if not rates:
        return

    if get_rate is None:
        total = sum(rate.split_rate for rate in rates)
    else:
        total = sum(get_rate(rate) for rate in rates)

    total = decimal.Decimal(total).quantize(Decimal("0.01"))

    if total != Decimal("100"):
        raise ValidationError(f"Total {label} must equal 100%. Got: {total}%")


def validate_split_rate_range[T](
    rates: Sequence[T],
    *,
    label: str = "split rate",
    context: str = "",
    get_rate: Any = None,
) -> None:
    from app.errors.common_errors import ValidationError

    for rate in rates:
        if get_rate is None:
            split_rate: Decimal = rate.split_rate  # type: ignore[attr-defined]
        else:
            split_rate = get_rate(rate)

        if split_rate < Decimal("0"):
            ctx = f" {context}" if context else ""
            raise ValidationError(
                f"{label.capitalize()} cannot be negative{ctx}. Got: {split_rate}%"
            )

        if split_rate > Decimal("100"):
            ctx = f" {context}" if context else ""
            raise ValidationError(
                f"{label.capitalize()} cannot exceed 100%{ctx}. Got: {split_rate}%"
            )


MAX_COMMISSION_RATE = Decimal("25")


def validate_commission_rate_max(
    items: Sequence[T],
    *,
    max_rate: Decimal = MAX_COMMISSION_RATE,
    label: str = "commission rate",
) -> None:
    for item in items:
        commission_rate = item.commission_rate
        if commission_rate > max_rate:
            raise ValidationError(
                f"{label.capitalize()} cannot exceed {max_rate}%. Got: {commission_rate}%"
            )
