from typing import Any

import orjson
from strawberry.types.scalar import ScalarDefinition


def serialize_json(value: dict[str, Any]) -> str:
    return orjson.dumps(
        value,
        default=lambda o: (
            str(o)
            if hasattr(o, "__class__") and "UUID" in o.__class__.__name__
            else None
        ),
    ).decode()


def parse_json(value: Any) -> dict[str, Any]:
    return orjson.loads(orjson.dumps(value))


JsonScalar = ScalarDefinition(
    name="JSON",
    description="The `JSON` scalar type represents JSON values as specified by ECMA-404",
    specified_by_url=None,
    serialize=serialize_json,
    parse_value=parse_json,
    parse_literal=None,
)
