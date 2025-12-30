import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_checks(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate checks from v5 (commission.checks) to v6 (pycommission.checks)."""
    logger.info("Starting check migration...")

    checks = await source.fetch("""
        SELECT
            c.id,
            c.check_number,
            c.entity_date,
            c.post_date,
            c.commission_month,
            COALESCE(c.commission, 0) as entered_commission_amount,
            c.factory_id,
            c.status + 1 AS status,
            c.creation_type,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM commission.checks c
        JOIN "user".users u ON u.id = c.created_by
    """)

    if not checks:
        logger.info("No checks to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.checks (
            id, check_number, entity_date, post_date, commission_month,
            entered_commission_amount, factory_id, status, creation_type,
            created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (id) DO UPDATE SET
            check_number = EXCLUDED.check_number,
            entity_date = EXCLUDED.entity_date,
            post_date = EXCLUDED.post_date,
            commission_month = EXCLUDED.commission_month,
            entered_commission_amount = EXCLUDED.entered_commission_amount,
            factory_id = EXCLUDED.factory_id,
            status = EXCLUDED.status,
            creation_type = EXCLUDED.creation_type
        """,
        [(
            c["id"],
            c["check_number"],
            c["entity_date"],
            c["post_date"],
            c["commission_month"],
            c["entered_commission_amount"],
            c["factory_id"],
            c["status"],
            c["creation_type"],
            c["created_by_id"],
            c["created_at"],
        ) for c in checks],
    )

    logger.info(f"Migrated {len(checks)} checks")
    return len(checks)


async def migrate_check_details(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate check details from v5 (commission.check_details) to v6 (pycommission.check_details).

    Maps v5 deduction_id to v6 credit_id (deductions were stored in credits table).
    """
    logger.info("Starting check detail migration...")

    details = await source.fetch("""
        SELECT
            cd.id,
            cd.check_id,
            cd.invoice_id,
            cd.adjustment_id,
            cd.deduction_id as credit_id,
            COALESCE(cd.applied_amount, 0) as applied_amount
        FROM commission.check_details cd
        JOIN commission.checks c ON c.id = cd.check_id
        JOIN "user".users u ON u.id = c.created_by
    """)

    if not details:
        logger.info("No check details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.check_details (
            id, check_id, invoice_id, adjustment_id, credit_id, applied_amount
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            check_id = EXCLUDED.check_id,
            invoice_id = EXCLUDED.invoice_id,
            adjustment_id = EXCLUDED.adjustment_id,
            credit_id = EXCLUDED.credit_id,
            applied_amount = EXCLUDED.applied_amount
        """,
        [(
            d["id"],
            d["check_id"],
            d["invoice_id"],
            d["adjustment_id"],
            d["credit_id"],
            d["applied_amount"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} check details")
    return len(details)
