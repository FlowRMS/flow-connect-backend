from typing import Any, NewType

import orjson
import strawberry


def create_json_scalar() -> Any:
    def serialize_json(value: dict[str, Any]) -> Any:
        return orjson.dumps(
            value,
            default=lambda o: str(o)
            if hasattr(o, "__class__") and "UUID" in o.__class__.__name__
            else None,
        ).decode()

    def parse_json(value: Any) -> Any:
        return orjson.loads(orjson.dumps(value))

    return strawberry.scalar(
        NewType("JSON", object),  # pyright: ignore[reportArgumentType]
        description="The `JSON` scalar type represents JSON values as specified by ECMA-404",
        serialize=serialize_json,
        parse_value=parse_json,
    )


JsonScalar = create_json_scalar()
