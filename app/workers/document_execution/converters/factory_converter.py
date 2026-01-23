from decimal import Decimal
from typing import Any, override
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.addresses.address import AddressSourceTypeEnum, AddressTypeEnum
from commons.db.v6.core.factories.factory import Factory
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.address_dto import AddressDTO
from commons.dtos.core.factory_dto import FactoryDTO
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.addresses.services.address_service import AddressService
from app.graphql.addresses.strawberry.address_input import AddressInput
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_input import FactoryInput
from app.graphql.v2.core.factories.strawberry.factory_split_rate_input import (
    FactorySplitRateInput,
)

from .base import BaseEntityConverter, BulkCreateResult, ConversionResult
from .entity_mapping import EntityMapping


class FactoryConverter(BaseEntityConverter[FactoryDTO, FactoryInput, Factory]):
    entity_type = DocumentEntityType.FACTORIES
    dto_class = FactoryDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        factory_service: FactoryService,
        address_service: AddressService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.factory_service = factory_service
        self.address_service = address_service
        self._address_cache: dict[str, AddressDTO] = {}

    @override
    def get_dedup_key(
        self,
        dto: FactoryDTO,
        entity_mapping: EntityMapping,
    ) -> tuple[Any, ...] | None:
        return (dto.factory_name,)

    @override
    async def create_entity(
        self,
        input_data: FactoryInput,
    ) -> Factory:
        return await self.factory_service.create(input_data)

    @override
    async def create_entities_bulk(
        self,
        inputs: list[FactoryInput],
    ) -> BulkCreateResult[Factory]:
        created: list[Factory] = []
        skipped: list[int] = []
        for i, inp in enumerate(inputs):
            try:
                entity = await self.create_entity(inp)
                created.append(entity)
            except Exception as e:
                logger.warning(f"Failed to create factory at index {i}: {e}")
                skipped.append(i)

        await self._create_addresses_for_factories(created)

        return BulkCreateResult(created=created, skipped_indices=skipped)

    async def _create_addresses_for_factories(
        self,
        factories: list[Factory],
    ) -> None:
        address_inputs: list[AddressInput] = []
        for factory in factories:
            addr_dto = self._address_cache.get(factory.title)
            if not addr_dto:
                continue
            if not addr_dto.address_line_one and not addr_dto.address_line_two:
                continue
            address_inputs.append(self._build_address_input(factory.id, addr_dto))

        if address_inputs:
            try:
                _ = await self.address_service.bulk_create(address_inputs)
            except Exception as e:
                logger.warning(f"Failed to bulk create addresses: {e}")

    def _build_address_input(
        self,
        factory_id: UUID,
        addr_dto: AddressDTO,
    ) -> AddressInput:
        return AddressInput(
            source_id=factory_id,
            source_type=AddressSourceTypeEnum.FACTORY,
            address_types=[AddressTypeEnum.SHIPPING, AddressTypeEnum.BILLING],
            line_1=addr_dto.address_line_one or addr_dto.address_line_two or "",
            line_2=addr_dto.address_line_two if addr_dto.address_line_one else None,
            city=addr_dto.city or "",
            state=addr_dto.state,
            zip_code=str(addr_dto.zip_code) if addr_dto.zip_code else "00000",
            country="US",
            is_primary=True,
        )

    @override
    async def to_input(
        self,
        dto: FactoryDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[FactoryInput]:
        if dto.address:
            self._address_cache[dto.factory_name] = dto.address

        split_rates = await self._build_split_rates(dto.inside_sales_rep_name)

        return ConversionResult.ok(
            FactoryInput(
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
