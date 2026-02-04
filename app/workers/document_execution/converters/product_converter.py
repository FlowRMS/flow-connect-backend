from dataclasses import dataclass
from decimal import Decimal
from typing import Any, override
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.core.products.product import Product
from commons.db.v6.core.products.product_uom import ProductUom
from commons.db.v6.warehouse.inventory import ABCClass, OwnershipType
from commons.db.v6.warehouse.inventory.inventory import Inventory
from commons.db.v6.warehouse.inventory.inventory_item import (
    InventoryItem,
    InventoryItemStatus,
)
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.core.product_dto import ProductDTO
from commons.graphql.models.enums.common_enums import CreationTypeEnum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.inventory.services.inventory_item_service import (
    InventoryItemService,
)
from app.graphql.v2.core.inventory.services.inventory_service import InventoryService
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
from .exceptions import (
    ConversionError,
    FactoryPartNumberRequiredError,
    FactoryRequiredError,
    WarehouseRequiredForInventoryError,
)


@dataclass(frozen=True)
class InventoryData:
    warehouse_id: UUID
    initial_quantity: Decimal | None = None
    lot_number: str | None = None
    ownership_type: OwnershipType = OwnershipType.CONSIGNMENT
    abc_class: ABCClass | None = None


@dataclass(frozen=True)
class ProductCreatePayload:
    product_input: ProductInput
    inventory_data: InventoryData | None = None


class ProductConverter(BaseEntityConverter[ProductDTO, ProductCreatePayload, Product]):
    entity_type = DocumentEntityType.PRODUCTS
    dto_class = ProductDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        product_service: ProductService,
        inventory_service: InventoryService,
        inventory_item_service: InventoryItemService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.product_service = product_service
        self.inventory_service = inventory_service
        self.inventory_item_service = inventory_item_service
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
        input_data: ProductCreatePayload,
    ) -> Product:
        product = await self.product_service.create(input_data.product_input)

        if input_data.inventory_data:
            _ = await self._create_inventory_for_product(
                product, input_data.inventory_data
            )

        return product

    async def _create_inventory_for_product(
        self,
        product: Product,
        inventory_data: InventoryData,
    ) -> Inventory:
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=inventory_data.warehouse_id,
            ownership_type=inventory_data.ownership_type,
            abc_class=inventory_data.abc_class,
        )
        created_inventory = await self.inventory_service.create(inventory)

        if inventory_data.initial_quantity and inventory_data.initial_quantity > 0:
            item = InventoryItem(
                inventory_id=created_inventory.id,
                quantity=inventory_data.initial_quantity,
                lot_number=inventory_data.lot_number,
                status=InventoryItemStatus.AVAILABLE,
            )
            _ = await self.inventory_item_service.add_item(item)

        return created_inventory

    @override
    async def create_entities_bulk(
        self,
        inputs: list[ProductCreatePayload],
    ) -> BulkCreateResult[Product]:
        product_inputs = [p.product_input for p in inputs]
        created = await self.product_service.bulk_create(product_inputs)
        created_keys = {(p.factory_part_number, p.factory_id) for p in created}

        created_map = {(p.factory_part_number, p.factory_id): p for p in created}
        for payload in inputs:
            if payload.inventory_data:
                key = (
                    payload.product_input.factory_part_number,
                    payload.product_input.factory_id,
                )
                product = created_map.get(key)
                if product:
                    _ = await self._create_inventory_for_product(
                        product, payload.inventory_data
                    )

        skipped = [
            i
            for i, inp in enumerate(inputs)
            if (inp.product_input.factory_part_number, inp.product_input.factory_id)
            not in created_keys
        ]
        return BulkCreateResult(created=created, skipped_indices=skipped)

    @override
    async def separate_inputs(
        self,
        inputs: list[ProductCreatePayload],
    ) -> SeparatedInputs[ProductCreatePayload]:
        if not inputs:
            return SeparatedInputs(
                for_creation=[],
                for_creation_indices=[],
                for_update=[],
                for_update_indices=[],
            )

        fpn_pairs = [
            (inp.product_input.factory_part_number, inp.product_input.factory_id)
            for inp in inputs
        ]
        existing_products = await self.product_service.get_existing_products(fpn_pairs)
        existing_map = {
            (p.factory_part_number, p.factory_id): p for p in existing_products
        }

        for_creation: list[ProductCreatePayload] = []
        for_creation_indices: list[int] = []
        for_update: list[tuple[ProductCreatePayload, Product]] = []
        for_update_indices: list[int] = []

        for i, inp in enumerate(inputs):
            key = (inp.product_input.factory_part_number, inp.product_input.factory_id)
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
        inputs_with_entities: list[tuple[ProductCreatePayload, Product]],
    ) -> BulkCreateResult[Product]:
        if not inputs_with_entities:
            return BulkCreateResult(created=[], skipped_indices=[])

        product_pairs = [
            (payload.product_input, existing)
            for payload, existing in inputs_with_entities
        ]
        updated = await self.product_service.bulk_update(product_pairs)
        updated_ids = {p.id for p in updated}

        for payload, existing in inputs_with_entities:
            if existing.id in updated_ids and payload.inventory_data:
                existing_inv = await self.inventory_service.get_by_product(
                    existing.id, payload.inventory_data.warehouse_id
                )
                if not existing_inv:
                    _ = await self._create_inventory_for_product(
                        existing, payload.inventory_data
                    )

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
    ) -> ConversionResult[ProductCreatePayload]:
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
            min_order_qty=Decimal(dto.min_order_quantity)
            if dto.min_order_quantity
            else None,
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

        inventory_data = self._build_inventory_data(dto, entity_mapping)
        if isinstance(inventory_data, ConversionError):
            return ConversionResult.fail(inventory_data)

        return ConversionResult.ok(
            ProductCreatePayload(
                product_input=product_input,
                inventory_data=inventory_data,
            )
        )

    def _build_inventory_data(
        self,
        dto: ProductDTO,
        entity_mapping: EntityMapping,
    ) -> InventoryData | ConversionError | None:
        if not dto.is_warehouse_product:
            return None

        warehouse_id = entity_mapping.warehouse_id
        if not warehouse_id:
            return WarehouseRequiredForInventoryError(dto.factory_part_number)

        return InventoryData(
            warehouse_id=warehouse_id,
            initial_quantity=dto.initial_quantity,
            lot_number=dto.lot_number,
            ownership_type=self._parse_ownership_type(dto.ownership_type),
            abc_class=self._parse_abc_class(dto.abc_class),
        )

    @staticmethod
    def _parse_ownership_type(value: str | None) -> OwnershipType:
        if not value:
            return OwnershipType.CONSIGNMENT
        mapping = {
            "CONSIGNMENT": OwnershipType.CONSIGNMENT,
            "OWNED": OwnershipType.OWNED,
            "THIRD_PARTY": OwnershipType.THIRD_PARTY,
        }
        return mapping.get(value.upper(), OwnershipType.CONSIGNMENT)

    @staticmethod
    def _parse_abc_class(value: str | None) -> ABCClass | None:
        if not value:
            return None
        mapping = {
            "A": ABCClass.A,
            "B": ABCClass.B,
            "C": ABCClass.C,
        }
        return mapping.get(value.upper())

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
