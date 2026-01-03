from decimal import Decimal
from typing import Any
from uuid import UUID

from commons.db.v6.ai.documents.enums import EntityType
from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.db.v6.commission.orders import Order, OrderBalance
from commons.dtos.order.order_dto import OrderDTO
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .converters.base import BaseEntityConverter
from .converters.registry import get_converter

CONFIRMED_STATUSES = frozenset(
    {
        ConfirmationStatus.CONFIRMED,
        ConfirmationStatus.AUTO_MATCHED,
        ConfirmationStatus.CREATED_NEW,
    }
)


class DocumentExecutorService:
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def execute(self, pending_document: PendingDocument) -> list[UUID]:
        if not pending_document.entity_type:
            raise ValueError("PendingDocument has no entity_type set")

        entity_mapping = self._build_entity_mapping(pending_document.pending_entities)
        logger.info(f"Built entity mapping with {len(entity_mapping)} entries")

        dtos = self._parse_dtos(pending_document)
        logger.info(f"Parsed {len(dtos)} DTOs from extracted_data_json")

        converter = get_converter(pending_document.entity_type, self.session)
        created_ids: list[UUID] = []

        for i, dto in enumerate(dtos):
            logger.info(f"Processing DTO {i + 1}/{len(dtos)}")
            entity_id = await self._create_entity(
                entity_type=pending_document.entity_type,
                converter=converter,
                dto=dto,
                entity_mapping=entity_mapping,
            )
            created_ids.append(entity_id)

        return created_ids

    def _build_entity_mapping(
        self,
        pending_entities: list[PendingEntity],
    ) -> dict[str, UUID]:
        mapping: dict[str, UUID] = {}

        for pe in pending_entities:
            if pe.confirmation_status not in CONFIRMED_STATUSES:
                continue

            if not pe.best_match_id:
                logger.warning(
                    f"PendingEntity {pe.id} is confirmed but has no best_match_id"
                )
                continue

            match pe.entity_type:
                case EntityPendingType.FACTORIES:
                    mapping["factory"] = pe.best_match_id
                case EntityPendingType.CUSTOMERS:
                    mapping["sold_to_customer"] = pe.best_match_id
                case EntityPendingType.BILL_TO_CUSTOMERS:
                    mapping["bill_to_customer"] = pe.best_match_id
                case EntityPendingType.PRODUCTS:
                    key = f"product_{pe.flow_index_detail}"
                    mapping[key] = pe.best_match_id
                case EntityPendingType.END_USERS:
                    key = f"end_user_{pe.flow_index_detail}"
                    mapping[key] = pe.best_match_id

        return mapping

    def _parse_dtos(self, pending_document: PendingDocument) -> list[Any]:
        if not pending_document.extracted_data_json:
            return []

        raw_dtos = BaseEntityConverter.parse_dtos_from_json(
            pending_document.extracted_data_json
        )

        match pending_document.entity_type:
            case EntityType.ORDERS:
                return [OrderDTO.model_validate(d) for d in raw_dtos]
            case _:
                raise ValueError(
                    f"Unsupported entity type: {pending_document.entity_type}"
                )

    async def _create_entity(
        self,
        entity_type: EntityType,
        converter: BaseEntityConverter[Any, Any],
        dto: Any,
        entity_mapping: dict[str, UUID],
    ) -> UUID:
        input_obj = await converter.to_input(dto, entity_mapping)

        match entity_type:
            case EntityType.ORDERS:
                return await self._create_order(input_obj)
            case _:
                raise ValueError(f"Unsupported entity type for creation: {entity_type}")

    async def _create_order(self, order_input: Any) -> UUID:
        order: Order = order_input.to_orm_model()
        balance = self._calculate_order_balance(order)
        self.session.add(balance)
        await self.session.flush([balance])

        order.balance_id = balance.id
        self.session.add(order)
        await self.session.flush([order])

        logger.info(f"Created order: {order.id} ({order.order_number})")
        return order.id

    def _calculate_order_balance(self, order: Order) -> OrderBalance:
        details = order.details
        quantity = sum((d.quantity for d in details), Decimal("0"))
        subtotal = sum((d.subtotal for d in details), Decimal("0"))
        discount = sum((d.discount for d in details), Decimal("0"))
        total = subtotal - discount
        commission = sum((d.commission for d in details), Decimal("0"))
        commission_discount = sum(
            (d.commission_discount for d in details), Decimal("0")
        )

        return OrderBalance(
            quantity=quantity,
            subtotal=subtotal,
            total=total,
            commission=commission,
            discount=discount,
            discount_rate=self._calc_rate(discount, subtotal),
            commission_rate=self._calc_rate(commission, total),
            commission_discount=commission_discount,
            commission_discount_rate=self._calc_rate(commission_discount, commission),
        )

    @staticmethod
    def _calc_rate(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0:
            return Decimal("0")
        return (numerator / denominator) * Decimal("100")
