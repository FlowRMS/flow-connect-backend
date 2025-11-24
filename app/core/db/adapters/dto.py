import abc
from collections.abc import Iterable
from typing import Generic, Protocol, Self, TypeVar

_TModel_contra = TypeVar("_TModel_contra", contravariant=True)
_TType = TypeVar("_TType")
_F = TypeVar("_F")


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
