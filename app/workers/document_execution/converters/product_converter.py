from decimal import Decimal
from typing import override
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.products.product import Product
from commons.db.v6.core.products.product_uom import ProductUom
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.product_dto import ProductDTO
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.products.services.product_service import ProductService
from app.graphql.v2.core.products.strawberry.product_cpn_input import (
    ProductCpnLiteInput,
)
from app.graphql.v2.core.products.strawberry.product_input import ProductInput

from .base import BaseEntityConverter
from .entity_mapping import EntityMapping


class ProductConverter(BaseEntityConverter[ProductDTO, ProductInput, Product]):
    entity_type = DocumentEntityType.PRODUCTS
    dto_class = ProductDTO
    _uom_cache: dict[str, UUID]

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        product_service: ProductService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.product_service = product_service
        self._uom_cache = {}

    @override
    async def create_entity(
        self,
        input_data: ProductInput,
    ) -> Product:
        product = await self.product_service.create(input_data)
        return product

    @override
    async def to_input(
        self,
        dto: ProductDTO,
        entity_mapping: EntityMapping,
    ) -> ProductInput:
        factory_id = entity_mapping.factory_id
        if not factory_id:
            raise ValueError("Factory ID is required but not found in entity_mapping")

        uom_id = await self._get_or_create_uom_id(dto.unit_of_measure)

        product_input = ProductInput(
            factory_part_number=dto.factory_part_number,
            factory_id=factory_id,
            product_uom_id=uom_id,
            unit_price=dto.unit_price or Decimal("0"),
            default_commission_rate=dto.commission_rate or Decimal("0"),
            published=dto.published or False,
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

        return product_input

    async def _get_or_create_uom_id(self, uom_title: str) -> UUID:
        title_upper = uom_title.upper()
        if title_upper in self._uom_cache:
            return self._uom_cache[title_upper]

        stmt = select(ProductUom).where(ProductUom.title == title_upper)
        result = await self.session.execute(stmt)
        uom = result.scalar_one_or_none()

        if uom:
            self._uom_cache[title_upper] = uom.id
            return uom.id

        new_uom = ProductUom(title=title_upper)
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
