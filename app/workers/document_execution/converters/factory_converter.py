from decimal import Decimal
from typing import override

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.factories.factory import Factory
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.factory_dto import FactoryDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_input import FactoryInput

from .base import BaseEntityConverter
from .entity_mapping import EntityMapping


class FactoryConverter(BaseEntityConverter[FactoryDTO, FactoryInput, Factory]):
    entity_type = DocumentEntityType.FACTORIES
    dto_class = FactoryDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        factory_service: FactoryService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.factory_service = factory_service

    @override
    async def create_entity(
        self,
        input_data: FactoryInput,
    ) -> Factory:
        return await self.factory_service.create(input_data)

    @override
    async def to_input(
        self,
        dto: FactoryDTO,
        entity_mapping: EntityMapping,
    ) -> FactoryInput:
        return FactoryInput(
            title=dto.factory_name,
            published=False,
            email=dto.email,
            phone=dto.phone,
            lead_time=self._parse_lead_time(dto.lead_time),
            payment_terms=dto.payment_terms,
            base_commission_rate=dto.base_commission or Decimal("0"),
            freight_terms=dto.freight_terms,
        )

    @staticmethod
    def _parse_lead_time(lead_time: str | None) -> int | None:
        if not lead_time:
            return None
        digits = "".join(c for c in lead_time if c.isdigit())
        return int(digits) if digits else None
