from decimal import Decimal
from uuid import UUID

from commons.db.v6.commission.orders import Order, OrderDetail, OrderStatus
from loguru import logger
from rapidfuzz import fuzz
from sqlalchemy.ext.asyncio import AsyncSession


class OrderDetailMatcherService:
    SIMILARITY_THRESHOLD = 88
    PRICE_TOLERANCE = Decimal("0.1")

    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def match_order_detail(
        self,
        order: Order,
        unit_price: Decimal,
        part_number: str | None,
        quantity: Decimal,
        item_number: int,
    ) -> UUID | None:
        if not order.details:
            return None

        candidates = self._build_candidates(order.details, part_number)
        logger.info(f"Built {len(candidates)} candidates for order detail matching")
        logger.info(f"Candidates: {candidates}")
        logger.info(
            f"Matching with unit_price={unit_price}, quantity={quantity}, item_number={item_number}, part_number={part_number}"
        )
        return self._find_best_match(
            candidates=candidates,
            unit_price=unit_price,
            quantity=quantity,
            item_number=item_number,
        )

    def _build_candidates(
        self,
        details: list[OrderDetail],
        part_number: str | None,
    ) -> list[dict]:
        candidates = []
        for detail in details:
            candidate = {
                "id": detail.id,
                "item_number": detail.item_number,
                "unit_price": detail.unit_price,
                "shipping_balance": detail.shipping_balance,
                "quantity": detail.quantity,
                "status": detail.status,
                "similarity_fpn": 0.0,
                "similarity_description": 0.0,
            }

            if part_number:
                fpn = (
                    detail.product.factory_part_number
                    if detail.product
                    else detail.product_name_adhoc or ""
                )
                desc = (
                    detail.product.description
                    if detail.product
                    else detail.product_description_adhoc or ""
                )
                desc = desc or ""
                candidate["similarity_fpn"] = fuzz.ratio(
                    part_number.lower(), fpn.lower()
                )
                candidate["similarity_description"] = fuzz.ratio(
                    part_number.lower(), desc.lower()
                )

            candidates.append(candidate)

        return candidates

    def _find_best_match(
        self,
        candidates: list[dict],
        unit_price: Decimal,
        quantity: Decimal,
        item_number: int,
    ) -> UUID | None:
        clauses = self._get_matching_clauses(unit_price, quantity, item_number)

        for clause_fn, allow_multiple in clauses:
            matches = [c for c in candidates if clause_fn(c)]
            if matches:
                if allow_multiple or len(matches) == 1:
                    best = max(matches, key=lambda c: c["shipping_balance"])
                    logger.debug(f"Matched order detail {best['id']} using clause")
                    return best["id"]

        logger.warning(
            "No order detail match found",
        )
        return None

    def _get_matching_clauses(
        self,
        unit_price: Decimal,
        quantity: Decimal,
        item_number: int,
    ) -> list[tuple]:
        threshold = self.SIMILARITY_THRESHOLD
        tolerance = self.PRICE_TOLERANCE

        def price_match(c: dict) -> bool:
            c_price = Decimal(str(c["unit_price"]))
            return c_price == unit_price or abs(c_price - unit_price) < tolerance

        def fpn_match(c: dict) -> bool:
            return c["similarity_fpn"] >= threshold

        def cpn_match(c: dict) -> bool:
            return c["similarity_description"] >= threshold

        def either_match(c: dict) -> bool:
            return fpn_match(c) or cpn_match(c)

        def item_match(c: dict) -> bool:
            return c["item_number"] == item_number

        def open_status(c: dict) -> bool:
            return c["status"] == OrderStatus.OPEN

        def quantity_valid(c: dict) -> bool:
            return Decimal(str(c["quantity"])) >= quantity

        return [
            (
                lambda c: item_match(c)
                and fpn_match(c)
                and open_status(c)
                and quantity_valid(c),
                False,
            ),
            (
                lambda c: price_match(c)
                and fpn_match(c)
                and open_status(c)
                and quantity_valid(c),
                False,
            ),
            (lambda c: price_match(c) and fpn_match(c) and quantity_valid(c), True),
            (lambda c: price_match(c) and fpn_match(c) and quantity_valid(c), False),
            (lambda c: price_match(c) and cpn_match(c) and quantity_valid(c), False),
            (lambda c: price_match(c) and either_match(c) and quantity_valid(c), True),
            (lambda c: price_match(c) and either_match(c) and quantity_valid(c), False),
            (lambda c: either_match(c) and quantity_valid(c), False),
            (lambda c: item_match(c) and either_match(c) and quantity_valid(c), False),
            (lambda c: price_match(c) and quantity_valid(c), True),
            (lambda c: item_match(c) and quantity_valid(c), False),
            (lambda c: quantity_valid(c), False),
        ]
