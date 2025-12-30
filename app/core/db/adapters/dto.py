import abc
import datetime
import decimal
import enum
import uuid
from collections.abc import Iterable
from typing import Any, Generic, Protocol, Self, TypeVar

import strawberry
from pydantic.alias_generators import to_snake
from sqlalchemy.engine.row import Row

_TModel_contra = TypeVar("_TModel_contra", contravariant=True)
_TType = TypeVar("_TType")
_F = TypeVar("_F")

DECIMAL_PRECISION: int = 2


class DTOMixinProtocol(Protocol[_TModel_contra, _TType]):
    @classmethod
    def from_orm_model_list(
        cls,
        models: Iterable[_TModel_contra],
    ) -> list[_TType]: ...


class DTOMixin(abc.ABC, Generic[_TModel_contra]):
    @classmethod
    @abc.abstractmethod
    def from_orm_model(cls, model: _TModel_contra) -> Self:
        raise NotImplementedError

    @classmethod
    def from_orm_model_optional(
        cls,
        model: _TModel_contra | None,
    ) -> Self | None:  # pragma: no cover
        return None if model is None else cls.from_orm_model(model)

    @classmethod
    def from_orm_model_list(cls, models: Iterable[_TModel_contra]) -> list[Self]:
        return [cls.from_orm_model(model) for model in models]  # pragma: no cover


class LandingPageBase:
    """Base class for landing page response types with serialization support."""

    def to_dict(self) -> dict[str, Any]:
        """Convert the instance to a dictionary for CSV export."""
        d: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                if isinstance(value, datetime.datetime):
                    d[key] = value.isoformat()
                elif isinstance(value, decimal.Decimal):
                    d[key] = round(value, DECIMAL_PRECISION)
                elif isinstance(value, enum.IntEnum):
                    d[key] = value.name.replace("_", " ").title()
                else:
                    d[key] = value
        return d

    @classmethod
    def unpack_row(cls, row: Row[Any]) -> dict[str, Any]:
        """Unpack a SQLAlchemy row into a dictionary with snake_case keys."""
        d = row._mapping  # pyright: ignore[reportPrivateUsage]
        return {to_snake(key): value for key, value in d.items()}


@strawberry.interface
class LandingPageInterfaceBase(LandingPageBase):
    """Base interface for landing page responses with common fields."""

    id: uuid.UUID
    created_at: datetime.datetime
    created_by: str
    user_ids: list[uuid.UUID]

    @classmethod
    def from_orm_model(cls, row: Row[Any]) -> Self:
        """Create an instance from a SQLAlchemy Row result."""
        return cls(**cls.unpack_row(row))

    @classmethod
    def from_orm_model_list(cls, rows: list[Row[Any]]) -> list[Self]:
        """Create a list of instances from SQLAlchemy Row results."""
        return [cls.from_orm_model(row) for row in rows]
