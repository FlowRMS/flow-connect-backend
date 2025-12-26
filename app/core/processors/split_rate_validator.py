from collections.abc import Sequence
from decimal import Decimal
from typing import Any


def validate_split_rates_sum_to_100[T](
    rates: Sequence[T],
    *,
    label: str = "split rates",
    get_rate: Any = None,
) -> None:
    from app.errors.common_errors import ValidationError

    if not rates:
        return

    if get_rate is None:
        total = sum(rate.split_rate for rate in rates)  # type: ignore[attr-defined]
    else:
        total = sum(get_rate(rate) for rate in rates)

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
