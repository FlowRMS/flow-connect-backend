import uuid
from typing import Any

import strawberry


def serialize_uuid(value: Any) -> str:
    return str(value)


def parse_uuid(value: str) -> uuid.UUID:
    if value is None or value == "":
        return None  # pyright: ignore[reportReturnType]
    return uuid.UUID(value)


IdScalar = strawberry.scalar(
    strawberry.ID,  # pyright: ignore[reportArgumentType]
    serialize=serialize_uuid,
    parse_value=parse_uuid,
)  # pyright: ignore[reportArgumentType]
