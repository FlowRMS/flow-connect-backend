"""
One-time script to backfill user_ids column for existing records.

Usage:
    uv run python scripts/backfill_user_ids.py

This populates user_ids for:
- Orders: created_by_id + inside_reps + split_rates
- Quotes: created_by_id + inside_reps + split_rates
- Invoices: created_by_id + split_rates
- Checks: created_by_id only
"""

import asyncio

from commons.db.controller import MultiTenantController
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import Settings


async def backfill_orders(session: AsyncSession) -> int:
    query = text("""
        UPDATE pycommission.orders o
        SET user_ids = subq.all_user_ids
        FROM (
            SELECT
                o2.id,
                ARRAY(
                    SELECT DISTINCT unnest(
                        ARRAY[o2.created_by_id] ||
                        COALESCE(
                            (SELECT array_agg(DISTINCT oir.user_id)
                             FROM pycommission.order_details od
                             JOIN pycommission.order_inside_reps oir ON oir.order_detail_id = od.id
                             WHERE od.order_id = o2.id),
                            ARRAY[]::uuid[]
                        ) ||
                        COALESCE(
                            (SELECT array_agg(DISTINCT osr.user_id)
                             FROM pycommission.order_details od
                             JOIN pycommission.order_split_rates osr ON osr.order_detail_id = od.id
                             WHERE od.order_id = o2.id),
                            ARRAY[]::uuid[]
                        )
                    )
                ) AS all_user_ids
            FROM pycommission.orders o2
        ) subq
        WHERE o.id = subq.id
          AND (o.user_ids IS NULL OR o.user_ids = ARRAY[]::uuid[])
    """)
    result = await session.execute(query)
    return result.rowcount or 0


async def backfill_quotes(session: AsyncSession) -> int:
    query = text("""
        UPDATE pycrm.quotes q
        SET user_ids = subq.all_user_ids
        FROM (
            SELECT
                q2.id,
                ARRAY(
                    SELECT DISTINCT unnest(
                        ARRAY[q2.created_by_id] ||
                        COALESCE(
                            (SELECT array_agg(DISTINCT qir.user_id)
                             FROM pycrm.quote_details qd
                             JOIN pycrm.quote_inside_reps qir ON qir.quote_detail_id = qd.id
                             WHERE qd.quote_id = q2.id),
                            ARRAY[]::uuid[]
                        ) ||
                        COALESCE(
                            (SELECT array_agg(DISTINCT qsr.user_id)
                             FROM pycrm.quote_details qd
                             JOIN pycrm.quote_split_rates qsr ON qsr.quote_detail_id = qd.id
                             WHERE qd.quote_id = q2.id),
                            ARRAY[]::uuid[]
                        )
                    )
                ) AS all_user_ids
            FROM pycrm.quotes q2
        ) subq
        WHERE q.id = subq.id
          AND (q.user_ids IS NULL OR q.user_ids = ARRAY[]::uuid[])
    """)
    result = await session.execute(query)
    return result.rowcount or 0


async def backfill_invoices(session: AsyncSession) -> int:
    query = text("""
        UPDATE pycommission.invoices i
        SET user_ids = subq.all_user_ids
        FROM (
            SELECT
                i2.id,
                ARRAY(
                    SELECT DISTINCT unnest(
                        ARRAY[i2.created_by_id] ||
                        COALESCE(
                            (SELECT array_agg(DISTINCT isr.user_id)
                             FROM pycommission.invoice_details id
                             JOIN pycommission.invoice_split_rates isr ON isr.invoice_detail_id = id.id
                             WHERE id.invoice_id = i2.id),
                            ARRAY[]::uuid[]
                        )
                    )
                ) AS all_user_ids
            FROM pycommission.invoices i2
        ) subq
        WHERE i.id = subq.id
          AND (i.user_ids IS NULL OR i.user_ids = ARRAY[]::uuid[])
    """)
    result = await session.execute(query)
    return result.rowcount or 0


async def backfill_checks(session: AsyncSession) -> int:
    query = text("""
        UPDATE pycommission.checks c
        SET user_ids = ARRAY[c.created_by_id]
        WHERE c.user_ids IS NULL OR c.user_ids = ARRAY[]::uuid[]
    """)
    result = await session.execute(query)
    return result.rowcount or 0


async def run_backfill_for_tenant(
    controller: MultiTenantController,
    tenant_name: str,
) -> dict[str, int]:
    async with controller.scoped_session(tenant_name) as session:
        async with session.begin():
            results = {
                "orders": await backfill_orders(session),
                "quotes": await backfill_quotes(session),
                "invoices": await backfill_invoices(session),
                "checks": await backfill_checks(session),
            }
    return results


async def main() -> None:
    settings = Settings()

    controller = MultiTenantController(
        pg_url=settings.pg_url.unicode_string(),
        app_name="Flow Py CRM - Backfill Script",
        echo=False,
        env=settings.environment,
    )

    async with controller:
        tenants = list(controller.engines.keys())

        print("Starting user_ids backfill...")
        print("=" * 60)
        print(f"Found {len(tenants)} tenant(s): {', '.join(tenants)}")

        for tenant_name in tenants:
            print(f"\nProcessing tenant: {tenant_name}")
            try:
                results = await run_backfill_for_tenant(controller, tenant_name)
                print(f"  Orders updated:   {results['orders']:,}")
                print(f"  Quotes updated:   {results['quotes']:,}")
                print(f"  Invoices updated: {results['invoices']:,}")
                print(f"  Checks updated:   {results['checks']:,}")
            except Exception as e:
                print(f"  ERROR: {e}")

    print("\n" + "=" * 60)
    print("Backfill complete!")


if __name__ == "__main__":
    asyncio.run(main())
