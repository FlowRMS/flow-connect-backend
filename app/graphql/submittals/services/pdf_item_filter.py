from decimal import Decimal

from commons.db.v6.crm.submittals import Submittal, SubmittalItem
from loguru import logger

from app.graphql.submittals.services.pdf_types import RolledUpItem

LAMPS_KEYWORDS = ("lamp", "lamps")
ACCESSORIES_KEYWORDS = ("accessor", "accessories", "accessory")
CQ_KEYWORDS = ("cq", "customer quoted")
KITS_KEYWORDS = ("kit", "kits")


def get_item_category_title(item: SubmittalItem) -> str | None:
    try:
        qd = item.quote_detail
        if qd is None:
            return None
        product = qd.product
        if product is None:
            return None
        category = product.category
        if category is None:
            return None
        return category.title
    except Exception:
        return None


def matches_category(title: str | None, keywords: tuple[str, ...]) -> bool:
    if not title:
        return False
    lower = title.lower().strip()
    return any(kw in lower for kw in keywords)


def is_item_from_order(item: SubmittalItem) -> bool:
    try:
        qd = item.quote_detail
        if qd is None:
            return False
        return qd.order_id is not None
    except Exception:
        return False


def apply_config_filters(
    items: list[SubmittalItem],
    submittal: Submittal,
) -> list[SubmittalItem | RolledUpItem]:
    filtered = list(items)

    if not submittal.config_include_lamps:
        before = len(filtered)
        filtered = [
            it
            for it in filtered
            if not matches_category(get_item_category_title(it), LAMPS_KEYWORDS)
        ]
        if len(filtered) != before:
            logger.info(f"Excluded {before - len(filtered)} lamp items")

    if not submittal.config_include_accessories:
        before = len(filtered)
        filtered = [
            it
            for it in filtered
            if not matches_category(get_item_category_title(it), ACCESSORIES_KEYWORDS)
        ]
        if len(filtered) != before:
            logger.info(f"Excluded {before - len(filtered)} accessory items")

    if not submittal.config_include_cq:
        before = len(filtered)
        filtered = [
            it
            for it in filtered
            if not matches_category(get_item_category_title(it), CQ_KEYWORDS)
        ]
        if len(filtered) != before:
            logger.info(f"Excluded {before - len(filtered)} CQ items")

    if not submittal.config_include_from_orders:
        before = len(filtered)
        filtered = [it for it in filtered if not is_item_from_order(it)]
        if len(filtered) != before:
            logger.info(f"Excluded {before - len(filtered)} from-order items")

    result: list[SubmittalItem | RolledUpItem] = []
    rollup_kits: list[SubmittalItem] = []
    rollup_accessories: list[SubmittalItem] = []

    for it in filtered:
        cat_title = get_item_category_title(it)
        if submittal.config_roll_up_kits and matches_category(cat_title, KITS_KEYWORDS):
            rollup_kits.append(it)
        elif submittal.config_roll_up_accessories and matches_category(
            cat_title, ACCESSORIES_KEYWORDS
        ):
            rollup_accessories.append(it)
        else:
            result.append(it)

    if rollup_kits:
        total_qty = sum((it.quantity or Decimal(0)) for it in rollup_kits)
        result.append(
            RolledUpItem(
                part_number="(Kits - Rolled Up)",
                description=f"{len(rollup_kits)} kit items consolidated",
                quantity=total_qty if total_qty else None,
                rolled_up_count=len(rollup_kits),
            )
        )
        logger.info(f"Rolled up {len(rollup_kits)} kit items into 1 summary row")

    if rollup_accessories:
        total_qty = sum((it.quantity or Decimal(0)) for it in rollup_accessories)
        result.append(
            RolledUpItem(
                part_number="(Accessories - Rolled Up)",
                description=f"{len(rollup_accessories)} accessory items consolidated",
                quantity=total_qty if total_qty else None,
                rolled_up_count=len(rollup_accessories),
            )
        )
        logger.info(
            f"Rolled up {len(rollup_accessories)} accessory items into 1 summary row"
        )

    return result
