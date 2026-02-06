import datetime

import pendulum
from strawberry.types.scalar import ScalarDefinition


def serialize_datetime(dt: pendulum.DateTime | datetime.datetime) -> str:
    try:
        return dt.isoformat()
    except ValueError:
        return dt.to_iso8601_string()  # pyright: ignore[reportAttributeAccessIssue]


def parse_datetime(value: str) -> pendulum.DateTime | datetime.datetime:
    return pendulum.parse(value)  # pyright: ignore[reportReturnType]


DateTimeScalar = ScalarDefinition(
    name="datetime",
    description="A date and time",
    specified_by_url=None,
    serialize=serialize_datetime,
    parse_value=parse_datetime,
    parse_literal=None,
)
