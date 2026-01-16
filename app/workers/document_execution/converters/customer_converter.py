from decimal import Decimal
from typing import Any, override
from uuid import UUID

from commons.db.v6 import Customer, RepTypeEnum
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.addresses.address import AddressSourceTypeEnum, AddressTypeEnum
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.address_dto import AddressDTO
from commons.dtos.core.customer_dto import CustomerDTO
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors.split_rate_validator import distribute_split_rates
from app.graphql.addresses.services.address_service import AddressService
from app.graphql.addresses.strawberry.address_input import AddressInput
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
        address_service: AddressService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.customer_service = customer_service
        self.address_service = address_service
        self._address_cache: dict[str, list[AddressDTO]] = {}

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

        await self._create_addresses_for_customers(created)

        return BulkCreateResult(created=created, skipped_indices=skipped)

    async def _create_addresses_for_customers(
        self,
        customers: list[Customer],
    ) -> None:
        address_inputs: list[AddressInput] = []
        for customer in customers:
            address_dtos = self._address_cache.get(customer.company_name, [])
            for i, addr_dto in enumerate(address_dtos):
                if not addr_dto.address_line_one and not addr_dto.address_line_two:
                    continue
                address_inputs.append(
                    self._build_address_input(customer.id, addr_dto, i)
                )

        if address_inputs:
            try:
                _ = await self.address_service.bulk_create(address_inputs)
            except Exception as e:
                logger.warning(f"Failed to bulk create addresses: {e}")

    def _build_address_input(
        self,
        customer_id: UUID,
        addr_dto: AddressDTO,
        position: int,
    ) -> AddressInput:
        return AddressInput(
            source_id=customer_id,
            source_type=AddressSourceTypeEnum.CUSTOMER,
            address_types=[AddressTypeEnum.SHIPPING, AddressTypeEnum.BILLING],
            line_1=addr_dto.address_line_one or addr_dto.address_line_two or "",
            line_2=addr_dto.address_line_two if addr_dto.address_line_one else None,
            city=addr_dto.city or "",
            state=addr_dto.state,
            zip_code=str(addr_dto.zip_code) if addr_dto.zip_code else "00000",
            country="US",
            is_primary=position == 0,
        )

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

        if dto.addresses:
            self._address_cache[dto.company_name] = dto.addresses

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

        split_rates: list[OutsideSplitRateInput] = []
        seen_user_ids: set[str] = set()

        for position, sales_rep in enumerate(dto.outside_sales_reps):
            user = await self.get_user_by_full_name(
                sales_rep.name_signature, RepTypeEnum.OUTSIDE
            )
            if not user:
                continue
            if str(user.id) in seen_user_ids:
                continue
            seen_user_ids.add(str(user.id))
            split_rates.append(
                OutsideSplitRateInput(
                    user_id=user.id,
                    split_rate=Decimal("0"),
                    # split_rate=sales_rep.split_rate or default_rates[position],
                    position=position,
                )
            )

        defaulted_split_rates = distribute_split_rates(len(split_rates))
        for i in range(len(split_rates)):
            split_rates[i].split_rate = defaulted_split_rates[i]

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
