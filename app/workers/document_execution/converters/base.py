from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from uuid import UUID

from commons.db.v6.ai.documents import PendingDocument
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.factories.factory import Factory
from commons.db.v6.user import User
from commons.dtos.common.dto_loader_service import DTOLoaderService, LoadedDTOs
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .exceptions import ConversionError

if TYPE_CHECKING:
    from .entity_mapping import EntityMapping

TDto = TypeVar("TDto", bound=BaseModel)
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")
T = TypeVar("T")

DEFAULT_BATCH_SIZE = 500


@dataclass
class ConversionResult(Generic[T]):
    value: T | None
    error: ConversionError | None

    @classmethod
    def ok(cls, value: T) -> "ConversionResult[T]":
        return cls(value=value, error=None)

    @classmethod
    def fail(cls, error: ConversionError) -> "ConversionResult[T]":
        return cls(value=None, error=error)

    def is_ok(self) -> bool:
        return self.error is None

    def is_error(self) -> bool:
        return self.error is not None

    def unwrap(self) -> T:
        if self.is_error():
            raise ValueError("Cannot unwrap a ConversionResult with an error")
        return self.value  # type: ignore[return-value]

    def unwrap_error(self) -> ConversionError:
        if self.is_ok():
            raise ValueError("Cannot unwrap_error a ConversionResult without an error")
        return self.error  # type: ignore[return-value]


@dataclass
class BulkCreateResult(Generic[TOutput]):
    created: list[TOutput]
    skipped_indices: list[int]


class BaseEntityConverter(ABC, Generic[TDto, TInput, TOutput]):
    entity_type: DocumentEntityType
    dto_class: type[BaseModel]

    def __init__(
        self, session: AsyncSession, dto_loader_service: DTOLoaderService
    ) -> None:
        super().__init__()
        self.session = session
        self.dto_loader_service = dto_loader_service
        self._factory_cache: dict[UUID, Factory] = {}
        self._user_cache: dict[str, User | None] = {}

    @abstractmethod
    async def create_entity(
        self,
        input_data: TInput,
    ) -> TOutput: ...

    @abstractmethod
    async def to_input(
        self,
        dto: TDto,
        entity_mapping: "EntityMapping",
    ) -> ConversionResult[TInput]: ...

    async def to_inputs_bulk(
        self,
        dtos: list[TDto],
        entity_mappings: list["EntityMapping"],
    ) -> list[TInput]:
        inputs: list[TInput] = []
        for dto, mapping in zip(dtos, entity_mappings, strict=True):
            result = await self.to_input(dto, mapping)
            if result.is_ok() and result.value is not None:
                inputs.append(result.value)
        return inputs

    async def create_entities_bulk(
        self,
        inputs: list[TInput],
    ) -> BulkCreateResult[TOutput]:
        created: list[TOutput] = []
        skipped: list[int] = []
        for i, inp in enumerate(inputs):
            try:
                entity = await self.create_entity(inp)
                created.append(entity)
            except Exception as e:
                logger.warning(f"Failed to create entity at index {i}: {e}")
                skipped.append(i)
        return BulkCreateResult(created=created, skipped_indices=skipped)

    async def get_factory(self, factory_id: UUID) -> Factory | None:
        if factory_id in self._factory_cache:
            return self._factory_cache[factory_id]

        stmt = select(Factory).where(Factory.id == factory_id)
        result = await self.session.execute(stmt)
        factory = result.scalar_one_or_none()

        if factory:
            self._factory_cache[factory_id] = factory

        return factory

    async def get_factory_commission_rate(self, factory_id: UUID) -> Decimal:
        factory = await self.get_factory(factory_id)
        if factory:
            return factory.base_commission_rate
        return Decimal("0")

    async def get_factory_commission_discount_rate(self, factory_id: UUID) -> Decimal:
        factory = await self.get_factory(factory_id)
        if factory:
            return factory.commission_discount_rate
        return Decimal("0")

    async def get_factory_discount_rate(self, factory_id: UUID) -> Decimal:
        factory = await self.get_factory(factory_id)
        if factory:
            return factory.overall_discount_rate
        return Decimal("0")

    async def get_user_by_full_name(self, full_name: str) -> User | None:
        cache_key = full_name.lower().strip()
        if cache_key in self._user_cache:
            return self._user_cache[cache_key]

        stmt = select(User).where(
            (func.lower(func.concat(User.first_name, " ", User.last_name)) == cache_key)
            | (func.lower(User.first_name) == cache_key)
            | (func.lower(User.last_name) == cache_key)
        )
        result = await self.session.execute(stmt)
        user = result.scalars().first()

        self._user_cache[cache_key] = user
        return user

    async def parse_dtos_from_json(
        self,
        pending_document: PendingDocument,
    ) -> LoadedDTOs:
        return await self.dto_loader_service.load_dtos_from_pending(pending_document)

    def get_dedup_key(
        self,
        dto: TDto,
        entity_mapping: "EntityMapping",
    ) -> tuple[Any, ...] | None:
        """
        Returns a hashable key for deduplication.
        Return None to skip deduplication for this converter.
        Override in subclasses to enable deduplication.
        """
        return None

    def deduplicate(
        self,
        dtos: list[TDto],
        entity_mappings: list["EntityMapping"],
    ) -> tuple[list[TDto], list["EntityMapping"]]:
        """
        Remove duplicates based on get_dedup_key.
        Keeps the first occurrence of each unique key.
        """
        seen: set[tuple[Any, ...]] = set()
        result_dtos: list[TDto] = []
        result_mappings: list["EntityMapping"] = []

        for dto, mapping in zip(dtos, entity_mappings, strict=True):
            key = self.get_dedup_key(dto, mapping)
            if key is None:
                result_dtos.append(dto)
                result_mappings.append(mapping)
            elif key not in seen:
                seen.add(key)
                result_dtos.append(dto)
                result_mappings.append(mapping)

        return result_dtos, result_mappings
