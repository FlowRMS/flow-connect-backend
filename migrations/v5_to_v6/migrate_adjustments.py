import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_adjustments(
    source: asyncpg.Connection, dest: asyncpg.Connection
) -> int:
    """Migrate adjustments from v5 (commission.expenses) to v6 (pycommission.adjustments).

    Only migrates expenses that have an associated check (to get factory_id).
    Allocation method is CUSTOMER (2) if sold_to_customer_id is present, otherwise REP_SPLIT (1).
    """
    logger.info("Starting adjustment migration...")

    adjustments = await source.fetch("""
        SELECT DISTINCT ON (e.id)
            e.id,
            e.expense_number as adjustment_number,
            e.entity_date,
            c.factory_id,
            e.sold_to_customer_id as customer_id,
            CASE
                WHEN e.sold_to_customer_id IS NOT NULL THEN 2
                ELSE 1
            END AS allocation_method,
            e.status + 1 AS status,
            COALESCE(e.expense_amount, 0) as amount,
            e.note as reason,
            e.creation_type,
            e.created_by as created_by_id,
            COALESCE(e.entry_date, now()) as created_at
        FROM commission.expenses e
        JOIN commission.check_details cd ON cd.adjustment_id = e.id
        JOIN commission.checks c ON c.id = cd.check_id
        WHERE c.factory_id IS NOT NULL
    """)

    if not adjustments:
        logger.info("No adjustments to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.adjustments (
            id, adjustment_number, entity_date, factory_id, customer_id,
            allocation_method, status, locked, amount, reason,
            creation_type, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, false, $8, $9, $10, $11, $12)
        ON CONFLICT (id) DO UPDATE SET
            adjustment_number = EXCLUDED.adjustment_number,
            entity_date = EXCLUDED.entity_date,
            factory_id = EXCLUDED.factory_id,
            customer_id = EXCLUDED.customer_id,
            allocation_method = EXCLUDED.allocation_method,
            status = EXCLUDED.status,
            amount = EXCLUDED.amount,
            reason = EXCLUDED.reason,
            creation_type = EXCLUDED.creation_type
        """,
        [
            (
                a["id"],
                a["adjustment_number"],
                a["entity_date"],
                a["factory_id"],
                a["customer_id"],
                a["allocation_method"],
                a["status"],
                a["amount"],
                a["reason"],
                a["creation_type"],
                a["created_by_id"],
                a["created_at"],
            )
            for a in adjustments
        ],
    )

    logger.info(f"Migrated {len(adjustments)} adjustments")
    return len(adjustments)


async def migrate_adjustment_split_rates(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate adjustment split rates from v5 (commission.expense_split_rates) to v6."""
    logger.info("Starting adjustment split rate migration...")

    split_rates = await source.fetch("""
        SELECT
            esr.id,
            esr.expense_id as adjustment_id,
            esr.user_id,
            COALESCE(esr.split_rate, 0) as split_rate,
            COALESCE(esr."position", 0) as position
        FROM commission.expense_split_rates esr
        JOIN commission.expenses e ON e.id = esr.expense_id
        JOIN commission.check_details cd ON cd.adjustment_id = e.id
        JOIN commission.checks c ON c.id = cd.check_id
        WHERE c.factory_id IS NOT NULL
    """)

    if not split_rates:
        logger.info("No adjustment split rates to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.adjustment_split_rates (
            id, adjustment_id, user_id, split_rate, "position"
        ) VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            adjustment_id = EXCLUDED.adjustment_id,
            user_id = EXCLUDED.user_id,
            split_rate = EXCLUDED.split_rate,
            "position" = EXCLUDED."position"
        """,
        [
            (
                sr["id"],
                sr["adjustment_id"],
                sr["user_id"],
                sr["split_rate"],
                sr["position"],
            )
            for sr in split_rates
        ],
    )

    logger.info(f"Migrated {len(split_rates)} adjustment split rates")
    return len(split_rates)
