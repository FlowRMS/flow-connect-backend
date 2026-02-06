import decimal
from typing import Any

from strawberry.types.scalar import ScalarDefinition


def serialize_decimal(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, str):
        value = decimal.Decimal(value)

    return str(round(value, 4))


def parse_decimal(value: str | None) -> decimal.Decimal | None:
    if value is None:
        return None

    return decimal.Decimal(value).quantize(decimal.Decimal("0.0001"))


DecimalScalar = ScalarDefinition(
    name="Decimal",
    description=None,
    specified_by_url=None,
    serialize=serialize_decimal,
    parse_value=parse_decimal,
    parse_literal=None,
)
