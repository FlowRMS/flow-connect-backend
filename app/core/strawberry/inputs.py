from abc import ABC
from collections.abc import Iterable
from typing import Any, Generic, Self, TypeVar

import strawberry

T = TypeVar("T")


class BaseInputGQL(ABC, Generic[T]):
    def to_orm_model(self, **kwargs: Any) -> T:
        """Convert GraphQL input to ORM model.

        Must be implemented by subclasses.

        Returns:
            ORM model instance
        """
        raise NotImplementedError(
            "to_orm_model method must be implemented in subclasses"
        )

    @classmethod
    def to_orm_model_list(cls, models: Iterable[Self]) -> list[T]:
        """Convert a list of GraphQL inputs to ORM models.

        Args:
            models: Iterable of GraphQL input instances

        Returns:
            List of ORM model instances
        """
        return [model.to_orm_model() for model in models]

    def is_id_set(self) -> bool:
        """Check if the ID is set to a value different from default.

        Returns:
            True if ID is set, False otherwise
        """
        if not hasattr(self, "id"):
            return False

        attr = getattr(self, "id")
        return attr not in (None, "", 0, "0")

    @staticmethod
    def optional_field(field: T, default: T | None = None) -> T | None:
        """Get optional field value or default.

        Args:
            field: Field value
            default: Default value if UNSET

        Returns:
            Field value or default
        """
        return default if field == strawberry.UNSET else field
