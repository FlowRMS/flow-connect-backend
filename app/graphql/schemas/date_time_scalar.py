import datetime
from typing import Any, Union

import pendulum
import strawberry


class DateTime:
    @staticmethod
    def serialize(dt: pendulum.DateTime | datetime.datetime) -> str:
        try:
            return dt.isoformat()
        except ValueError:
            return dt.to_iso8601_string()  # pyright: ignore[reportAttributeAccessIssue]

    @staticmethod
    def parse_value(value: str) -> pendulum.DateTime | datetime.datetime:
        return pendulum.parse(value)  # pyright: ignore[reportReturnType]


DateTimeScalar: Any = strawberry.scalar(
    Union[pendulum.DateTime, datetime.datetime],  # pyright: ignore[reportArgumentType]
    name="datetime",
    description="A date and time",
    serialize=DateTime.serialize,
    parse_value=DateTime.parse_value,
)
