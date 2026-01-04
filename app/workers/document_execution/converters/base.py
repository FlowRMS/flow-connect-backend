from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Generic, TypeVar
from uuid import UUID

from commons.db.v6.ai.documents import PendingDocument
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.factories.factory import Factory
from commons.dtos.common.dto_loader_service import DTOLoaderService, LoadedDTOs
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

TDto = TypeVar("TDto")
TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class BaseEntityConverter(ABC, Generic[TDto, TInput, TOutput]):
    entity_type: DocumentEntityType

    def __init__(
        self, session: AsyncSession, dto_loader_service: DTOLoaderService
    ) -> None:
        super().__init__()
        self.session = session
        self.dto_loader_service = dto_loader_service
        self._factory_cache: dict[UUID, Factory] = {}

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
        entity_mapping: dict[str, UUID],
    ) -> TInput:
        """
        Convert a DTO from commons to a Strawberry input using confirmed entity IDs.

        Args:
            dto: The extracted DTO from PendingDocument.extracted_data_json
            entity_mapping: Map of entity keys to confirmed UUIDs
                - "factory": Factory UUID
                - "sold_to_customer": Sold-to customer UUID
                - "bill_to_customer": Bill-to customer UUID (optional)
                - "product_{index}": Product UUID for line item at index
                - "end_user_{index}": End user UUID for line item at index

        Returns:
            Strawberry input ready for service creation
        """
        ...

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

    async def parse_dtos_from_json(
        self,
        pending_document: PendingDocument,
    ) -> LoadedDTOs:
        return await self.dto_loader_service.load_dtos_from_pending(pending_document)
