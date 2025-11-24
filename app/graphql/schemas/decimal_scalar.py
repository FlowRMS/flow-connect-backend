import decimal
from typing import Any

import strawberry


def serialize_decimal(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, str):
        value = decimal.Decimal(value)

    return str(round(value, 4))


def parse_decimal(value: str | None) -> decimal.Decimal | None:
    if value is None:
        return None

    return decimal.Decimal(value)


DecimalScalar = strawberry.scalar(
    decimal.Decimal,
    serialize=serialize_decimal,
    parse_value=parse_decimal,
)
