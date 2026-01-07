import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_credit_balances(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate credit balances from v5 (commission.credit_balances) to v6 (pycommission.credit_balances)."""
    logger.info("Starting credit balance migration...")

    balances = await source.fetch("""
        SELECT
            cb.id,
            COALESCE(cb.quantity, 0) as quantity,
            COALESCE(cb.subtotal, 0) as subtotal,
            COALESCE(cb.total, 0) as total,
            COALESCE(cb.commission, 0) as commission
        FROM commission.credit_balances cb
    """)

    if not balances:
        logger.info("No credit balances to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.credit_balances (
            id, quantity, subtotal, total, commission
        ) VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            quantity = EXCLUDED.quantity,
            subtotal = EXCLUDED.subtotal,
            total = EXCLUDED.total,
            commission = EXCLUDED.commission
        """,
        [(
            b["id"],
            b["quantity"],
            b["subtotal"],
            b["total"],
            b["commission"],
        ) for b in balances],
    )

    logger.info(f"Migrated {len(balances)} credit balances")
    return len(balances)


async def migrate_credits(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate credits from v5 (commission.credits) to v6 (pycommission.credits)."""
    logger.info("Starting credit migration...")

    credits = await source.fetch("""
        SELECT
            c.id,
            c.credit_number,
            c.order_id,
            c.entity_date,
            c.creation_type,
            c.status + 1 AS status,
            c.balance_id,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM commission.credits c
        JOIN commission.orders o ON o.id = c.order_id
        JOIN "user".users u ON u.id = c.created_by
        WHERE o.sold_to_customer_id IS NOT NULL
    """)

    if not credits:
        logger.info("No credits to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.credits (
            id, credit_number, order_id, entity_date, reason, locked,
            creation_type, status, credit_type, balance_id, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, NULL, false, $5, $6, 5, $7, $8, $9)
        ON CONFLICT (id) DO UPDATE SET
            credit_number = EXCLUDED.credit_number,
            order_id = EXCLUDED.order_id,
            entity_date = EXCLUDED.entity_date,
            creation_type = EXCLUDED.creation_type,
            status = EXCLUDED.status
        """,
        [(
            c["id"],
            c["credit_number"],
            c["order_id"],
            c["entity_date"],
            c["creation_type"],
            c["status"],
            c["balance_id"],
            c["created_by_id"],
            c["created_at"],
        ) for c in credits],
    )

    logger.info(f"Migrated {len(credits)} credits")
    return len(credits)


async def migrate_credit_details(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate credit details from v5 (commission.credit_details) to v6 (pycommission.credit_details)."""
    logger.info("Starting credit detail migration...")

    details = await source.fetch("""
        SELECT
            cd.id,
            cd.credit_id,
            cd.order_detail_id,
            cd.status + 1 AS status,
            ROW_NUMBER() OVER (PARTITION BY cd.credit_id ORDER BY cd.id) as item_number,
            COALESCE(cd.quantity, 0) as quantity,
            COALESCE(cd.unit_price, 0) as unit_price,
            COALESCE(cd.subtotal, 0) as subtotal,
            COALESCE(cd.total, 0) as total,
            COALESCE(cd.commission_rate, 0) as commission_rate,
            COALESCE(cd.commission, 0) as commission
        FROM commission.credit_details cd
        JOIN commission.credits c ON c.id = cd.credit_id
        JOIN commission.orders o ON o.id = c.order_id
        JOIN "user".users u ON u.id = c.created_by
        WHERE o.sold_to_customer_id IS NOT NULL
    """)

    if not details:
        logger.info("No credit details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.credit_details (
            id, credit_id, order_detail_id, status, item_number,
            quantity, unit_price, subtotal, total, commission_rate, commission
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (id) DO UPDATE SET
            credit_id = EXCLUDED.credit_id,
            order_detail_id = EXCLUDED.order_detail_id,
            status = EXCLUDED.status,
            item_number = EXCLUDED.item_number,
            quantity = EXCLUDED.quantity,
            unit_price = EXCLUDED.unit_price,
            subtotal = EXCLUDED.subtotal,
            total = EXCLUDED.total,
            commission_rate = EXCLUDED.commission_rate,
            commission = EXCLUDED.commission
        """,
        [(
            d["id"],
            d["credit_id"],
            d["order_detail_id"],
            d["status"],
            d["item_number"],
            d["quantity"],
            d["unit_price"],
            d["subtotal"],
            d["total"],
            d["commission_rate"],
            d["commission"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} credit details")
    return len(details)


async def migrate_credit_split_rates(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate credit split rates from v5 (commission.credit_split_rates) to v6 (pycommission.credit_split_rates)."""
    logger.info("Starting credit split rate migration...")

    split_rates = await source.fetch("""
        SELECT
            osr.id,
            cd.id as credit_detail_id,
            osr.user_id,
            COALESCE(osr.split_rate, 0) as split_rate,
            COALESCE(osr."position", 0) as position,
            COALESCE(osr.entry_date, now()) as created_at
        FROM commission.order_split_rates osr
        JOIN commission.credit_details cd ON cd.order_detail_id = osr.order_detail_id
        JOIN "user".users u ON u.id = osr.user_id
    """)

    if not split_rates:
        logger.info("No credit split rates to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.credit_split_rates (
            id, credit_detail_id, user_id, split_rate, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            credit_detail_id = EXCLUDED.credit_detail_id,
            user_id = EXCLUDED.user_id,
            split_rate = EXCLUDED.split_rate,
            "position" = EXCLUDED."position"
        """,
        [(
            sr["id"],
            sr["credit_detail_id"],
            sr["user_id"],
            sr["split_rate"],
            sr["position"],
            sr["created_at"],
        ) for sr in split_rates],
    )

    logger.info(f"Migrated {len(split_rates)} credit split rates")
    return len(split_rates)
