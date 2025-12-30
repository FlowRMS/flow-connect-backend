import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_invoice_balances(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate invoice balances from v5 (commission.invoice_balances) to v6 (pycommission.invoice_balances)."""
    logger.info("Starting invoice balance migration...")

    balances = await source.fetch("""
        SELECT
            ib.id,
            COALESCE(ib.quantity, 0) as quantity,
            COALESCE(ib.subtotal, 0) as subtotal,
            COALESCE(ib.total, 0) as total,
            COALESCE(ib.commission, 0) as commission,
            0 as discount,
            0 as discount_rate,
            COALESCE(ib.commission_rate, 0) as commission_rate,
            COALESCE(ib.commission_discount, 0) as commission_discount,
            COALESCE(ib.commission_discount_rate, 0) as commission_discount_rate
        FROM commission.invoice_balances ib
    """)

    if not balances:
        logger.info("No invoice balances to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.invoice_balances (
            id, quantity, subtotal, total, commission, discount,
            discount_rate, commission_rate, commission_discount,
            commission_discount_rate, paid_balance
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 0)
        ON CONFLICT (id) DO UPDATE SET
            quantity = EXCLUDED.quantity,
            subtotal = EXCLUDED.subtotal,
            total = EXCLUDED.total,
            commission = EXCLUDED.commission,
            discount = EXCLUDED.discount,
            discount_rate = EXCLUDED.discount_rate,
            commission_rate = EXCLUDED.commission_rate,
            commission_discount = EXCLUDED.commission_discount,
            commission_discount_rate = EXCLUDED.commission_discount_rate
        """,
        [(
            b["id"],
            b["quantity"],
            b["subtotal"],
            b["total"],
            b["commission"],
            b["discount"],
            b["discount_rate"],
            b["commission_rate"],
            b["commission_discount"],
            b["commission_discount_rate"],
        ) for b in balances],
    )

    logger.info(f"Migrated {len(balances)} invoice balances")
    return len(balances)


async def migrate_invoices(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate invoices from v5 (commission.invoices) to v6 (pycommission.invoices)."""
    logger.info("Starting invoice migration...")

    invoices = await source.fetch("""
        SELECT
            i.id,
            i.invoice_number,
            i.order_id,
            i.entity_date,
            i.due_date,
            i.published,
            i.locked,
            i.creation_type,
            i.status + 1 AS status,
            i.balance_id,
            i.created_by as created_by_id,
            COALESCE(i.entry_date, now()) as created_at
        FROM commission.invoices i
        JOIN commission.orders o ON o.id = i.order_id
        JOIN "user".users u ON u.id = i.created_by
        WHERE o.sold_to_customer_id IS NOT NULL
    """)

    if not invoices:
        logger.info("No invoices to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.invoices (
            id, invoice_number, order_id, entity_date, due_date,
            published, locked, creation_type, status, balance_id,
            created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        ON CONFLICT (id) DO UPDATE SET
            invoice_number = EXCLUDED.invoice_number,
            order_id = EXCLUDED.order_id,
            entity_date = EXCLUDED.entity_date,
            due_date = EXCLUDED.due_date,
            published = EXCLUDED.published,
            locked = EXCLUDED.locked,
            creation_type = EXCLUDED.creation_type,
            status = EXCLUDED.status
        """,
        [(
            inv["id"],
            inv["invoice_number"],
            inv["order_id"],
            inv["entity_date"],
            inv["due_date"],
            inv["published"],
            inv["locked"],
            inv["creation_type"],
            inv["status"],
            inv["balance_id"],
            inv["created_by_id"],
            inv["created_at"],
        ) for inv in invoices],
    )

    logger.info(f"Migrated {len(invoices)} invoices")
    return len(invoices)


async def migrate_invoice_details(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate invoice details from v5 (commission.invoice_details) to v6 (pycommission.invoice_details)."""
    logger.info("Starting invoice detail migration...")

    details = await source.fetch("""
        SELECT
            id.id,
            id.invoice_id,
            id.item_number,
            COALESCE(id.quantity, 0) as quantity,
            COALESCE(id.unit_price, 0) as unit_price,
            COALESCE(id.subtotal, 0) as subtotal,
            COALESCE(id.total, 0) as total,
            COALESCE(id.commission, 0) as total_line_commission,
            COALESCE(id.commission_rate, 0) as commission_rate,
            COALESCE(id.commission, 0) as commission,
            COALESCE(id.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(id.commission_discount, 0) as commission_discount,
            COALESCE(id.discount_rate, 0) as discount_rate,
            COALESCE(id.discount, 0) as discount,
            id.order_detail_id,
            id.status + 1 AS status,
            CASE
                WHEN id.uom_multiply AND id.uom_multiply_by > 0 THEN id.uom_multiply_by
                ELSE NULL
            END AS division_factor
        FROM commission.invoice_details id
        JOIN commission.invoices i ON i.id = id.invoice_id
        JOIN commission.orders o ON o.id = i.order_id
        JOIN commission.order_details od ON od.id = id.order_detail_id
        JOIN "user".users u ON u.id = i.created_by
        WHERE o.sold_to_customer_id IS NOT NULL
    """)

    if not details:
        logger.info("No invoice details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.invoice_details (
            id, invoice_id, item_number, quantity, unit_price, subtotal, total,
            total_line_commission, commission_rate, commission, commission_discount_rate,
            commission_discount, discount_rate, discount, order_detail_id, status,
            division_factor, invoiced_balance, product_id, product_name_adhoc,
            product_description_adhoc, uom_id, end_user_id, lead_time, note
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, 0, NULL, NULL, NULL, NULL, NULL, NULL, NULL)
        ON CONFLICT (id) DO UPDATE SET
            invoice_id = EXCLUDED.invoice_id,
            item_number = EXCLUDED.item_number,
            quantity = EXCLUDED.quantity,
            unit_price = EXCLUDED.unit_price,
            subtotal = EXCLUDED.subtotal,
            total = EXCLUDED.total,
            total_line_commission = EXCLUDED.total_line_commission,
            commission_rate = EXCLUDED.commission_rate,
            commission = EXCLUDED.commission,
            commission_discount_rate = EXCLUDED.commission_discount_rate,
            commission_discount = EXCLUDED.commission_discount,
            discount_rate = EXCLUDED.discount_rate,
            discount = EXCLUDED.discount,
            order_detail_id = EXCLUDED.order_detail_id,
            status = EXCLUDED.status,
            division_factor = EXCLUDED.division_factor
        """,
        [(
            d["id"],
            d["invoice_id"],
            d["item_number"],
            d["quantity"],
            d["unit_price"],
            d["subtotal"],
            d["total"],
            d["total_line_commission"],
            d["commission_rate"],
            d["commission"],
            d["commission_discount_rate"],
            d["commission_discount"],
            d["discount_rate"],
            d["discount"],
            d["order_detail_id"],
            d["status"],
            d["division_factor"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} invoice details")
    return len(details)
