from decimal import Decimal
from typing import override

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.factories.factory import Factory
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.factory_dto import FactoryDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_input import FactoryInput
from app.graphql.v2.core.factories.strawberry.factory_split_rate_input import (
    FactorySplitRateInput,
)

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
        split_rates = await self._build_split_rates(dto.inside_sales_rep_name)

        return FactoryInput(
            title=dto.factory_name,
            published=True,
            email=dto.email,
            phone=dto.phone,
            lead_time=self._parse_lead_time(dto.lead_time),
            payment_terms=dto.payment_terms,
            base_commission_rate=dto.base_commission or Decimal("0"),
            freight_terms=dto.freight_terms,
            split_rates=split_rates,
        )

    async def _build_split_rates(
        self,
        inside_sales_rep_name: str | None,
    ) -> list[FactorySplitRateInput]:
        if not inside_sales_rep_name:
            return []

        user = await self.get_user_by_full_name(inside_sales_rep_name)
        if not user:
            return []

        return [
            FactorySplitRateInput(
                user_id=user.id,
                split_rate=Decimal("100"),
                position=1,
            )
        ]

    @staticmethod
    def _parse_lead_time(lead_time: str | None) -> int | None:
        if not lead_time:
            return None
        digits = "".join(c for c in lead_time if c.isdigit())
        return int(digits) if digits else None
