from typing import TYPE_CHECKING, Callable

from commons.db.v6.ai.documents.enums import EntityType

if TYPE_CHECKING:
    from .base import BaseEntityConverter

_CONVERTER_REGISTRY: dict[EntityType, type["BaseEntityConverter"]] = {}


def register_converter(
    entity_type: EntityType,
) -> Callable[[type["BaseEntityConverter"]], type["BaseEntityConverter"]]:
    def decorator(cls: type["BaseEntityConverter"]) -> type["BaseEntityConverter"]:
        _CONVERTER_REGISTRY[entity_type] = cls
        return cls

    return decorator


def get_converter(entity_type: EntityType) -> "BaseEntityConverter":
    _ensure_converters_loaded()

    converter_class = _CONVERTER_REGISTRY.get(entity_type)
    if not converter_class:
        raise ValueError(f"No converter registered for entity type: {entity_type}")
    return converter_class()


def _ensure_converters_loaded() -> None:
    if not _CONVERTER_REGISTRY:
        from . import order_converter as _  # noqa: F401


def list_registered_converters() -> list[EntityType]:
    _ensure_converters_loaded()
    return list(_CONVERTER_REGISTRY.keys())
