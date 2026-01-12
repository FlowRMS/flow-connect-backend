from decimal import Decimal
from typing import Any, override
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.products.product import Product
from commons.db.v6.core.products.product_uom import ProductUom
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.product_dto import ProductDTO
from commons.graphql.models.enums.common_enums import CreationTypeEnum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.products.services.product_service import ProductService
from app.graphql.v2.core.products.strawberry.product_cpn_input import (
    ProductCpnLiteInput,
)
from app.graphql.v2.core.products.strawberry.product_input import ProductInput

from .base import (
    BaseEntityConverter,
    BulkCreateResult,
    ConversionResult,
    SeparatedInputs,
)
from .entity_mapping import EntityMapping
from .exceptions import FactoryPartNumberRequiredError, FactoryRequiredError


class ProductConverter(BaseEntityConverter[ProductDTO, ProductInput, Product]):
    entity_type = DocumentEntityType.PRODUCTS
    dto_class = ProductDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        product_service: ProductService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.product_service = product_service
        self._uom_cache: dict[str, UUID] = {}

    @override
    def get_dedup_key(
        self,
        dto: ProductDTO,
        entity_mapping: EntityMapping,
    ) -> tuple[Any, ...] | None:
        return (dto.factory_part_number, entity_mapping.factory_id)

    @override
    async def create_entity(
        self,
        input_data: ProductInput,
    ) -> Product:
        product = await self.product_service.create(input_data)
        return product

    @override
    async def create_entities_bulk(
        self,
        inputs: list[ProductInput],
    ) -> BulkCreateResult[Product]:
        created = await self.product_service.bulk_create(inputs)
        created_keys = {(p.factory_part_number, p.factory_id) for p in created}
        skipped = [
            i
            for i, inp in enumerate(inputs)
            if (inp.factory_part_number, inp.factory_id) not in created_keys
        ]
        return BulkCreateResult(created=created, skipped_indices=skipped)

    @override
    async def separate_inputs(
        self,
        inputs: list[ProductInput],
    ) -> SeparatedInputs[ProductInput]:
        if not inputs:
            return SeparatedInputs(
                for_creation=[],
                for_creation_indices=[],
                for_update=[],
                for_update_indices=[],
            )

        fpn_pairs = [(inp.factory_part_number, inp.factory_id) for inp in inputs]
        existing_products = await self.product_service.get_existing_products(fpn_pairs)
        existing_map = {
            (p.factory_part_number, p.factory_id): p for p in existing_products
        }

        for_creation: list[ProductInput] = []
        for_creation_indices: list[int] = []
        for_update: list[tuple[ProductInput, Product]] = []
        for_update_indices: list[int] = []

        for i, inp in enumerate(inputs):
            key = (inp.factory_part_number, inp.factory_id)
            existing = existing_map.get(key)
            if existing:
                for_update.append((inp, existing))
                for_update_indices.append(i)
            else:
                for_creation.append(inp)
                for_creation_indices.append(i)

        return SeparatedInputs(
            for_creation=for_creation,
            for_creation_indices=for_creation_indices,
            for_update=for_update,
            for_update_indices=for_update_indices,
        )

    @override
    async def update_entities_bulk(
        self,
        inputs_with_entities: list[tuple[ProductInput, Product]],
    ) -> BulkCreateResult[Product]:
        if not inputs_with_entities:
            return BulkCreateResult(created=[], skipped_indices=[])

        updated = await self.product_service.bulk_update(inputs_with_entities)
        updated_ids = {p.id for p in updated}
        skipped = [
            i
            for i, (_, existing) in enumerate(inputs_with_entities)
            if existing.id not in updated_ids
        ]
        return BulkCreateResult(created=updated, skipped_indices=skipped)

    @override
    async def to_input(
        self,
        dto: ProductDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[ProductInput]:
        factory_id = entity_mapping.factory_id
        if not factory_id:
            return ConversionResult.fail(FactoryRequiredError())

        if not dto.factory_part_number:
            return ConversionResult.fail(
                FactoryPartNumberRequiredError(dto.description)
            )

        uom_id = await self._get_or_create_uom_id(dto.unit_of_measure)

        product_input = ProductInput(
            factory_part_number=dto.factory_part_number,
            factory_id=factory_id,
            product_uom_id=uom_id,
            unit_price=dto.unit_price or Decimal("0"),
            default_commission_rate=dto.commission_rate or Decimal("0"),
            published=dto.published or True,
            description=dto.description,
            upc=dto.upc,
            min_order_qty=Decimal(dto.min_order_qty) if dto.min_order_qty else None,
            lead_time=self._parse_lead_time(dto.lead_time),
            unit_price_discount_rate=dto.overall_discount_rate,
            commission_discount_rate=dto.commission_discount_rate,
            approval_needed=dto.approval_needed,
            approval_date=dto.approval_date,
            approval_comments=dto.approval_comments,
        )

        if (
            dto.cpn
            and dto.cpn.customer_part_number
            and entity_mapping.sold_to_customer_id
        ):
            product_input.cpns = [
                ProductCpnLiteInput(
                    customer_id=entity_mapping.sold_to_customer_id,
                    customer_part_number=dto.cpn.customer_part_number,
                    unit_price=dto.cpn.unit_price or Decimal("0"),
                    commission_rate=dto.cpn.commission_rate or Decimal("0"),
                )
            ]

        return ConversionResult.ok(product_input)

    async def _get_or_create_uom_id(self, uom_title: str | None) -> UUID:
        title_upper = (uom_title or "EA").upper()
        if title_upper in self._uom_cache:
            return self._uom_cache[title_upper]

        stmt = select(ProductUom).where(ProductUom.title == title_upper)
        result = await self.session.execute(stmt)
        uom = result.scalar_one_or_none()

        if uom:
            self._uom_cache[title_upper] = uom.id
            return uom.id

        new_uom = ProductUom(
            title=title_upper,
            division_factor=Decimal("1"),
            creation_type=CreationTypeEnum.FLOW_BOT,
        )
        self.session.add(new_uom)
        await self.session.flush([new_uom])
        self._uom_cache[title_upper] = new_uom.id
        return new_uom.id

    @staticmethod
    def _parse_lead_time(lead_time: str | None) -> int | None:
        if not lead_time:
            return None
        digits = "".join(c for c in lead_time if c.isdigit())
        return int(digits) if digits else None
