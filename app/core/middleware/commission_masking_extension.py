from collections.abc import AsyncGenerator
from typing import Any, override

from strawberry.extensions import SchemaExtension

from app.core.context import Context
from app.graphql.v2.rbac.commission_fields import COMMISSION_FIELDS


def _mask_dict_recursive(data: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for key, value in data.items():
        if (
            key in COMMISSION_FIELDS
            or key.lower().endswith("commission")
            or key.lower().endswith("commissions")
            or "commission" in key.lower()
        ):
            if isinstance(value, bool):
                result[key] = False
            elif isinstance(value, (int, float)):
                result[key] = 0
            else:
                result[key] = None
        elif isinstance(value, dict):
            result[key] = _mask_dict_recursive(value)
        elif isinstance(value, list):
            result[key] = [
                _mask_dict_recursive(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


class CommissionMaskingExtension(SchemaExtension):
    @override
    async def on_execute(self) -> AsyncGenerator[None, None]:
        context: Context = self.execution_context.context
        yield
        if not context.commission_visible:
            result = self.execution_context.result
            if result and result.data:
                data = _mask_dict_recursive(result.data)
                result.data = data
