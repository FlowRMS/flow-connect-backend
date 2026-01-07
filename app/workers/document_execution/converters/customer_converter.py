from typing import Any, override

from commons.db.v6 import Customer
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.customer_dto import CustomerDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.customers.services.customer_service import CustomerService
from app.graphql.v2.core.customers.strawberry.customer_input import CustomerInput

from .base import BaseEntityConverter, BulkCreateResult
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
    ) -> CustomerInput:
        return CustomerInput(
            company_name=dto.company_name,
            published=True,
            is_parent=False,
            parent_id=None,
        )
