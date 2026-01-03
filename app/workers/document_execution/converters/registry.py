from typing import Any

from commons.db.v6.ai.documents.enums import EntityType
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseEntityConverter
from .order_converter import OrderConverter

CONVERTER_REGISTRY: dict[EntityType, type[BaseEntityConverter[Any, Any]]] = {
    EntityType.ORDERS: OrderConverter,
}


def get_converter(
    entity_type: EntityType,
    session: AsyncSession,
) -> BaseEntityConverter[Any, Any]:
    converter_class = CONVERTER_REGISTRY.get(entity_type)
    if not converter_class:
        raise ValueError(f"No converter registered for entity type: {entity_type}")
    return converter_class(session)


def list_registered_converters() -> list[EntityType]:
    return list(CONVERTER_REGISTRY.keys())
