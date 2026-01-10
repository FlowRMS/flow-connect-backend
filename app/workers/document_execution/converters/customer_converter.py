from decimal import Decimal
from typing import Any, override

from commons.db.v6 import Customer, RepTypeEnum
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.customer_dto import CustomerDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors.split_rate_validator import distribute_split_rates
from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_input import CustomerInput
from app.graphql.v2.core.customers.strawberry.customer_split_rate_input import (
    InsideSplitRateInput,
    OutsideSplitRateInput,
)
from app.workers.document_execution.converters.exceptions import ConversionError

from .base import BaseEntityConverter, BulkCreateResult, ConversionResult
from .entity_mapping import EntityMapping


class CustomerConverter(BaseEntityConverter[CustomerDTO, CustomerInput, Customer]):
    entity_type = DocumentEntityType.CUSTOMERS
    dto_class = CustomerDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        customer_service: CustomerService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.customer_service = customer_service

    @override
    def get_dedup_key(
        self,
        dto: CustomerDTO,
        entity_mapping: EntityMapping,
    ) -> tuple[Any, ...] | None:
        return (dto.company_name,)

    @override
    async def create_entity(
        self,
        input_data: CustomerInput,
    ) -> Customer:
        return await self.customer_service.create(input_data)

    @override
    async def create_entities_bulk(
        self,
        inputs: list[CustomerInput],
    ) -> BulkCreateResult[Customer]:
        created = await self.customer_service.bulk_create(inputs)
        created_names = {c.company_name for c in created}
        skipped = [
            i for i, inp in enumerate(inputs) if inp.company_name not in created_names
        ]
        return BulkCreateResult(created=created, skipped_indices=skipped)

    @override
    async def to_input(
        self,
        dto: CustomerDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[CustomerInput]:
        if not dto.company_name:
            return ConversionResult.fail(
                ConversionError("CustomerDTO missing company_name")
            )

        outside_split_rates = await self._build_outside_split_rates(dto)
        inside_split_rates = await self._build_inside_split_rates(dto)

        return ConversionResult.ok(
            CustomerInput(
                company_name=dto.company_name,
                published=True,
                is_parent=False,
                parent_id=None,
                outside_split_rates=outside_split_rates,
                inside_split_rates=inside_split_rates,
            )
        )

    async def _build_outside_split_rates(
        self,
        dto: CustomerDTO,
    ) -> list[OutsideSplitRateInput]:
        if not dto.outside_sales_reps:
            return []

        default_rates = distribute_split_rates(len(dto.outside_sales_reps))
        split_rates: list[OutsideSplitRateInput] = []

        for position, sales_rep in enumerate(dto.outside_sales_reps):
            user = await self.get_user_by_full_name(
                sales_rep.name_signature, RepTypeEnum.OUTSIDE
            )
            if not user:
                continue
            split_rates.append(
                OutsideSplitRateInput(
                    user_id=user.id,
                    split_rate=sales_rep.split_rate or default_rates[position],
                    position=position,
                )
            )
        return split_rates

    async def _build_inside_split_rates(
        self,
        dto: CustomerDTO,
    ) -> list[InsideSplitRateInput]:
        if not dto.inside_sales_rep_name:
            return []
        user = await self.get_user_by_full_name(
            dto.inside_sales_rep_name, RepTypeEnum.INSIDE
        )
        if not user:
            return []
        return [
            InsideSplitRateInput(
                user_id=user.id,
                split_rate=Decimal("100"),
                position=0,
            )
        ]
