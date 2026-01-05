from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING, Generic, TypeVar
from uuid import UUID

from commons.db.v6.ai.documents import PendingDocument
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.factories.factory import Factory
from commons.db.v6.user import User
from commons.dtos.common.dto_loader_service import DTOLoaderService, LoadedDTOs
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from .entity_mapping import EntityMapping

TDto = TypeVar("TDto", bound=BaseModel)
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


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
    ) -> TOutput:
        """
        Create the entity in the system using the provided input data.

        Args:
            input_data: The Strawberry input data for entity creation
        Returns:
            The created ORM entity
        """
        ...

    @abstractmethod
    async def to_input(
        self,
        dto: TDto,
        entity_mapping: "EntityMapping",
    ) -> TInput: ...

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
