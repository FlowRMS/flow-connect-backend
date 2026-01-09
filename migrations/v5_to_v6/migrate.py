import asyncio
import logging
from dataclasses import dataclass

import asyncpg

from migrations.v5_to_v6.migrate_customer_relations import (
    migrate_addresses,
    migrate_contact_links,
    migrate_contacts,
    migrate_customer_factory_sales_reps,
    migrate_inside_customer_split_rates,
    migrate_customer_split_rates,
    migrate_factory_split_rates,
)
from migrations.v5_to_v6.migrate_adjustments import (
    migrate_adjustment_split_rates,
    migrate_adjustments,
)
from migrations.v5_to_v6.migrate_ai import AI_TABLES, migrate_ai_table
from migrations.v5_to_v6.migrate_checks import (
    migrate_check_details,
    migrate_checks,
)
from migrations.v5_to_v6.migrate_files import (
    migrate_files,
    migrate_folders,
)
from migrations.v5_to_v6.migrate_credits import (
    migrate_credit_balances,
    migrate_credit_details,
    migrate_credit_split_rates,
    migrate_credits,
)
from migrations.v5_to_v6.migrate_invoices import (
    migrate_invoice_balances,
    migrate_invoice_details,
    migrate_invoice_split_rates,
    migrate_invoices,
)
from migrations.v5_to_v6.migrate_orders import (
    migrate_order_acknowledgements,
    migrate_order_balances,
    migrate_order_details,
    migrate_order_inside_reps,
    migrate_order_split_rates,
    migrate_orders,
)
from migrations.v5_to_v6.migrate_pycrm_entities import (
    migrate_companies,
    migrate_link_relations,
    migrate_notes,
    migrate_tasks,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class MigrationConfig:
    source_dsn: str
    dest_dsn: str
    batch_size: int = 500


async def migrate_users(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate users from v5 (user.users) to v6 (pyuser.users)."""
    logger.info("Starting user migration...")

    users = await source.fetch("""
        SELECT
            u.id,
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            u.keycloak_id::text as auth_provider_id,
            CASE
                WHEN ur.name = 'admin' THEN 1
                WHEN ur.name = 'manager' THEN 2
                WHEN ur.name = 'sales_rep' THEN 3
                ELSE 4
            END AS role,
            u.enabled,
            COALESCE(u.inside, false) as inside,
            COALESCE(u.outside, false) as outside,
            COALESCE(u.entry_date, now()) as created_at
        FROM "user".users u
        LEFT JOIN "user".user_roles ur ON u.role_id = ur.id
    """)

    if not users:
        logger.info("No users to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pyuser.users (
            id, username, first_name, last_name, email,
            auth_provider_id, role, enabled, inside, outside, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            email = EXCLUDED.email,
            auth_provider_id = EXCLUDED.auth_provider_id,
            role = EXCLUDED.role,
            enabled = EXCLUDED.enabled,
            inside = EXCLUDED.inside,
            outside = EXCLUDED.outside
        """,
        [(
            u["id"],
            u["username"],
            u["first_name"],
            u["last_name"],
            u["email"],
            u["auth_provider_id"],
            u["role"],
            u["enabled"],
            u["inside"],
            u["outside"],
            u["created_at"],
        ) for u in users],
    )

    logger.info(f"Migrated {len(users)} users")
    return len(users)


async def migrate_customers(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate customers from v5 (core.customers) to v6 (pycore.customers)."""
    logger.info("Starting customer migration...")

    # First, get customers without parents
    parent_customers = await source.fetch("""
        SELECT
            c.id,
            c.company_name,
            c.published,
            c.is_parent,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM core.customers c
        WHERE c.parent_id IS NULL
    """)

    # Insert parent customers first
    if parent_customers:
        await dest.executemany(
            """
            INSERT INTO pycore.customers (
                id, company_name, parent_id, published, is_parent, created_by_id, created_at
            ) VALUES ($1, $2, NULL, $3, $4, $5, $6)
            ON CONFLICT (id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                published = EXCLUDED.published,
                is_parent = EXCLUDED.is_parent
            """,
            [(
                c["id"],
                c["company_name"],
                c["published"],
                c["is_parent"],
                c["created_by_id"],
                c["created_at"],
            ) for c in parent_customers],
        )

    # Then get and insert child customers
    child_customers = await source.fetch("""
        SELECT
            c.id,
            c.company_name,
            c.parent_id,
            c.published,
            c.is_parent,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM core.customers c
        WHERE c.parent_id IS NOT NULL
    """)

    if child_customers:
        await dest.executemany(
            """
            INSERT INTO pycore.customers (
                id, company_name, parent_id, published, is_parent, created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                parent_id = EXCLUDED.parent_id,
                published = EXCLUDED.published,
                is_parent = EXCLUDED.is_parent
            """,
            [(
                c["id"],
                c["company_name"],
                c["parent_id"],
                c["published"],
                c["is_parent"],
                c["created_by_id"],
                c["created_at"],
            ) for c in child_customers],
        )

    total = len(parent_customers) + len(child_customers)
    logger.info(f"Migrated {total} customers ({len(parent_customers)} parents, {len(child_customers)} children)")
    return total


async def migrate_factories(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate factories from v5 (core.factories) to v6 (pycore.factories)."""
    logger.info("Starting factory migration...")

    factories = await source.fetch(r"""
        SELECT
            f.id,
            f.title,
            f.account_number,
            f.email,
            f.phone,
            CASE
                WHEN f.lead_time ~ '^\d+$' THEN f.lead_time::integer
                ELSE NULL
            END AS lead_time,
            CASE
                WHEN f.payment_terms ~ '^\d+$' THEN f.payment_terms::integer
                ELSE NULL
            END AS payment_terms,
            COALESCE(f.commission_rate, 0) as base_commission_rate,
            COALESCE(f.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(f.overall_discount_rate, 0) as overall_discount_rate,
            f.additional_information,
            f.freight_terms,
            f.external_payment_terms,
            f.published,
            f.freight_discount_type,
            f.creation_type,
            f.created_by as created_by_id,
            COALESCE(f.entry_date, now()) as created_at
        FROM core.factories f
    """)

    if not factories:
        logger.info("No factories to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.factories (
            id, title, account_number, email, phone, logo_id,
            lead_time, payment_terms, base_commission_rate,
            commission_discount_rate, overall_discount_rate,
            additional_information, freight_terms, external_payment_terms,
            published, freight_discount_type, creation_type,
            created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, NULL, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            account_number = EXCLUDED.account_number,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone,
            lead_time = EXCLUDED.lead_time,
            payment_terms = EXCLUDED.payment_terms,
            base_commission_rate = EXCLUDED.base_commission_rate,
            commission_discount_rate = EXCLUDED.commission_discount_rate,
            overall_discount_rate = EXCLUDED.overall_discount_rate,
            additional_information = EXCLUDED.additional_information,
            freight_terms = EXCLUDED.freight_terms,
            external_payment_terms = EXCLUDED.external_payment_terms,
            published = EXCLUDED.published,
            freight_discount_type = EXCLUDED.freight_discount_type,
            creation_type = EXCLUDED.creation_type
        """,
        [(
            f["id"],
            f["title"],
            f["account_number"],
            f["email"],
            f["phone"],
            f["lead_time"],
            f["payment_terms"],
            f["base_commission_rate"],
            f["commission_discount_rate"],
            f["overall_discount_rate"],
            f["additional_information"],
            f["freight_terms"],
            f["external_payment_terms"],
            f["published"],
            f["freight_discount_type"],
            f["creation_type"],
            f["created_by_id"],
            f["created_at"],
        ) for f in factories],
    )

    logger.info(f"Migrated {len(factories)} factories")
    return len(factories)


async def migrate_product_uoms(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate product UOMs from v5 (core.product_uoms) to v6 (pycore.product_uoms)."""
    logger.info("Starting product UOM migration...")

    uoms = await source.fetch("""
        SELECT
            u.id,
            u.title,
            u.description,
            u.creation_type,
            u.created_by as created_by_id,
            COALESCE(u.entry_date, now()) as created_at,
            CASE
                WHEN u.multiply AND u.multiply_by > 0 THEN u.multiply_by
                ELSE 1
            END AS division_factor
        FROM core.product_uoms u
    """)

    if not uoms:
        logger.info("No product UOMs to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.product_uoms (
            id, title, description, creation_type, created_at, division_factor
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            creation_type = EXCLUDED.creation_type,
            division_factor = EXCLUDED.division_factor
        """,
        [(
            u["id"],
            u["title"],
            u["description"],
            u["creation_type"],
            u["created_at"],
            u["division_factor"],
        ) for u in uoms],
    )

    logger.info(f"Migrated {len(uoms)} product UOMs")
    return len(uoms)


async def migrate_product_categories(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate product categories from v5 (core.product_categories) to v6 (pycore.product_categories)."""
    logger.info("Starting product category migration...")

    categories = await source.fetch("""
        SELECT
            pc.id,
            pc.title,
            COALESCE(pc.commission_rate, 0) as commission_rate,
            pc.factory_id
        FROM core.product_categories pc
    """)

    if not categories:
        logger.info("No product categories to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.product_categories (
            id, title, commission_rate, factory_id, parent_id, grandparent_id
        ) VALUES ($1, $2, $3, $4, NULL, NULL)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            commission_rate = EXCLUDED.commission_rate,
            factory_id = EXCLUDED.factory_id
        """,
        [(
            c["id"],
            c["title"],
            c["commission_rate"],
            c["factory_id"],
        ) for c in categories],
    )

    logger.info(f"Migrated {len(categories)} product categories")
    return len(categories)


async def migrate_products(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate products from v5 (core.products) to v6 (pycore.products)."""
    logger.info("Starting product migration...")

    products = await source.fetch(r"""
        SELECT
            p.id,
            p.factory_part_number,
            COALESCE(p.unit_price, 0) as unit_price,
            COALESCE(p.default_commission_rate, 0) as default_commission_rate,
            p.factory_id,
            p.product_category_id,
            p.product_uom_id,
            p.published,
            COALESCE(p.approval_needed, false) as approval_needed,
            p.description,
            p.creation_type,
            COALESCE(p.entry_date, now()) as created_at,
            p.created_by as created_by_id,
            p.individual_upc as upc,
            p.min_order_qty,
            CASE
                WHEN p.lead_time ~ '^\d+$' THEN p.lead_time::integer
                ELSE NULL
            END AS lead_time,
            p.overall_discount_rate as unit_price_discount_rate,
            p.commission_discount_rate,
            p.approval_date,
            p.approval_comments
        FROM core.products p
    """)

    if not products:
        logger.info("No products to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.products (
            id, factory_part_number, unit_price, default_commission_rate,
            factory_id, product_category_id, product_uom_id, published,
            approval_needed, description, creation_type, created_at,
            created_by_id, upc, default_divisor, min_order_qty, lead_time,
            unit_price_discount_rate, commission_discount_rate,
            approval_date, approval_comments, tags
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NULL, $15, $16, $17, $18, $19, $20, NULL)
        ON CONFLICT (id) DO UPDATE SET
            factory_part_number = EXCLUDED.factory_part_number,
            unit_price = EXCLUDED.unit_price,
            default_commission_rate = EXCLUDED.default_commission_rate,
            factory_id = EXCLUDED.factory_id,
            product_category_id = EXCLUDED.product_category_id,
            product_uom_id = EXCLUDED.product_uom_id,
            published = EXCLUDED.published,
            approval_needed = EXCLUDED.approval_needed,
            description = EXCLUDED.description,
            creation_type = EXCLUDED.creation_type,
            upc = EXCLUDED.upc,
            min_order_qty = EXCLUDED.min_order_qty,
            lead_time = EXCLUDED.lead_time,
            unit_price_discount_rate = EXCLUDED.unit_price_discount_rate,
            commission_discount_rate = EXCLUDED.commission_discount_rate,
            approval_date = EXCLUDED.approval_date,
            approval_comments = EXCLUDED.approval_comments
        """,
        [(
            p["id"],
            p["factory_part_number"],
            p["unit_price"],
            p["default_commission_rate"],
            p["factory_id"],
            p["product_category_id"],
            p["product_uom_id"],
            p["published"],
            p["approval_needed"],
            p["description"],
            p["creation_type"],
            p["created_at"],
            p["created_by_id"],
            p["upc"],
            p["min_order_qty"],
            p["lead_time"],
            p["unit_price_discount_rate"],
            p["commission_discount_rate"],
            p["approval_date"],
            p["approval_comments"],
        ) for p in products],
    )

    logger.info(f"Migrated {len(products)} products")
    return len(products)


async def migrate_product_cpns(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate product CPNs from v5 (core.product_cpns) to v6 (pycore.product_cpns)."""
    logger.info("Starting product CPN migration...")

    cpns = await source.fetch("""
        SELECT
            c.id,
            c.customer_part_number,
            COALESCE(c.unit_price, 0) as unit_price,
            COALESCE(c.commission_rate, 0) as commission_rate,
            c.product_id,
            c.customer_id
        FROM core.product_cpns c
    """)

    if not cpns:
        logger.info("No product CPNs to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.product_cpns (
            id, customer_part_number, unit_price, commission_rate, product_id, customer_id
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            customer_part_number = EXCLUDED.customer_part_number,
            unit_price = EXCLUDED.unit_price,
            commission_rate = EXCLUDED.commission_rate,
            product_id = EXCLUDED.product_id,
            customer_id = EXCLUDED.customer_id
        """,
        [(
            c["id"],
            c["customer_part_number"],
            c["unit_price"],
            c["commission_rate"],
            c["product_id"],
            c["customer_id"],
        ) for c in cpns],
    )

    logger.info(f"Migrated {len(cpns)} product CPNs")
    return len(cpns)


async def migrate_job_statuses(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate job statuses from v5 (crm.jobs.status) to v6 (pycrm.job_statuses)."""
    logger.info("Starting job status migration...")

    # Get unique statuses from v5 jobs
    statuses = await source.fetch("""
        SELECT DISTINCT j.status
        FROM crm.jobs j
        WHERE j.status IS NOT NULL
    """)

    # Create default statuses if none exist
    default_statuses = ["Open", "In Progress", "Closed"]
    status_names = [s["status"] for s in statuses] if statuses else []

    # Add defaults if not present
    for default in default_statuses:
        if default not in status_names:
            status_names.append(default)

    if not status_names:
        logger.info("No job statuses to migrate")
        return 0

    # Check which statuses already exist in destination
    existing = await dest.fetch("SELECT name FROM pycrm.job_statuses")
    existing_names = {e["name"] for e in existing}

    new_statuses = [name for name in status_names if name not in existing_names]

    if new_statuses:
        await dest.executemany(
            """
            INSERT INTO pycrm.job_statuses (id, name)
            VALUES (gen_random_uuid(), $1)
            ON CONFLICT DO NOTHING
            """,
            [(name,) for name in new_statuses],
        )

    logger.info(f"Migrated {len(new_statuses)} job statuses (total: {len(status_names)})")
    return len(new_statuses)


async def migrate_jobs(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate jobs from v5 (crm.jobs) to v6 (pycrm.jobs)."""
    logger.info("Starting job migration...")

    # First get status mapping from destination
    status_mapping = await dest.fetch("SELECT id, name FROM pycrm.job_statuses")
    status_map = {s["name"]: s["id"] for s in status_mapping}

    # Default to 'Open' status if not found
    default_status_id = status_map.get("Open")

    jobs = await source.fetch("""
        SELECT
            j.id,
            j.job_name,
            j.status,
            j.start_date,
            j.end_date,
            j.description,
            j.requester_id,
            j.job_owner_id,
            j.created_by as created_by_id,
            COALESCE(j.entry_date, now()) as created_at
        FROM crm.jobs j
    """)

    if not jobs:
        logger.info("No jobs to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.jobs (
            id, job_name, status_id, start_date, end_date, job_type,
            structural_details, structural_information, additional_information,
            description, requester_id, job_owner_id, tags, created_at, created_by_id
        ) VALUES ($1, $2, $3, $4, $5, NULL, NULL, NULL, NULL, $6, $7, $8, NULL, $9, $10)
        ON CONFLICT (id) DO UPDATE SET
            job_name = EXCLUDED.job_name,
            status_id = EXCLUDED.status_id,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date,
            description = EXCLUDED.description,
            requester_id = EXCLUDED.requester_id,
            job_owner_id = EXCLUDED.job_owner_id
        """,
        [(
            j["id"],
            j["job_name"],
            status_map.get(j["status"], default_status_id),
            j["start_date"],
            j["end_date"],
            j["description"],
            j["requester_id"],
            j["job_owner_id"],
            j["created_at"],
            j["created_by_id"],
        ) for j in jobs],
    )

    logger.info(f"Migrated {len(jobs)} jobs")
    return len(jobs)


async def migrate_quote_balances(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quote balances from v5 (crm.quote_balances) to v6 (pycrm.quote_balances)."""
    logger.info("Starting quote balance migration...")

    balances = await source.fetch("""
        SELECT
            qb.id,
            COALESCE(qb.quantity, 0) as quantity,
            COALESCE(qb.subtotal, 0) as subtotal,
            COALESCE(qb.total, 0) as total,
            COALESCE(qb.commission, 0) as commission,
            COALESCE(qb.discount, 0) as discount,
            COALESCE(qb.discount_rate, 0) as discount_rate,
            COALESCE(qb.commission_rate, 0) as commission_rate,
            COALESCE(qb.commission_discount, 0) as commission_discount,
            COALESCE(qb.commission_discount_rate, 0) as commission_discount_rate
        FROM crm.quote_balances qb
    """)

    if not balances:
        logger.info("No quote balances to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.quote_balances (
            id, quantity, subtotal, total, commission, discount,
            discount_rate, commission_rate, commission_discount, commission_discount_rate
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
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

    logger.info(f"Migrated {len(balances)} quote balances")
    return len(balances)


async def migrate_quote_lost_reasons(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quote lost reasons from v5 (crm.quote_lost_reasons) to v6 (pycrm.quote_lost_reasons)."""
    logger.info("Starting quote lost reason migration...")

    reasons = await source.fetch("""
        SELECT
            qlr.id,
            qlr.created_by as created_by_id,
            qlr.title,
            COALESCE(qlr."position", 0) as position,
            COALESCE(qlr.entry_date, now()) as created_at
        FROM crm.quote_lost_reasons qlr
    """)

    if not reasons:
        logger.info("No quote lost reasons to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.quote_lost_reasons (
            id, created_by_id, title, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            created_by_id = EXCLUDED.created_by_id,
            title = EXCLUDED.title,
            "position" = EXCLUDED."position"
        """,
        [(
            r["id"],
            r["created_by_id"],
            r["title"],
            r["position"],
            r["created_at"],
        ) for r in reasons],
    )

    logger.info(f"Migrated {len(reasons)} quote lost reasons")
    return len(reasons)


async def migrate_quotes(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quotes from v5 (crm.quotes) to v6 (pycrm.quotes)."""
    logger.info("Starting quote migration...")

    quotes = await source.fetch("""
        SELECT
            q.id,
            q.quote_number,
            q.entity_date,
            q.sold_to_customer_id,
            q.bill_to_customer_id,
            q.published,
            q.creation_type,
            q.status + 1 AS status,
            q.payment_terms,
            q.customer_ref,
            q.freight_terms,
            q.exp_date,
            q.revise_date,
            q.accept_date,
            COALESCE(q.blanket, false) as blanket,
            q.duplicated_from,
            q.balance_id,
            q.created_by as created_by_id,
            COALESCE(q.entry_date, now()) as created_at,
            q.job_id
        FROM crm.quotes q
        WHERE
            q.sold_to_customer_id IS NOT NULL
    """)

    if not quotes:
        logger.info("No quotes to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.quotes (
            id, quote_number, entity_date, sold_to_customer_id, bill_to_customer_id,
            published, creation_type, status, pipeline_stage, payment_terms,
            customer_ref, freight_terms, exp_date, revise_date, accept_date,
            blanket, duplicated_from, version_of, balance_id, created_by_id,
            created_at, job_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 0, $9, $10, $11, $12, $13, $14, $15, $16, NULL, $17, $18, $19, $20)
        ON CONFLICT (id) DO UPDATE SET
            quote_number = EXCLUDED.quote_number,
            entity_date = EXCLUDED.entity_date,
            sold_to_customer_id = EXCLUDED.sold_to_customer_id,
            bill_to_customer_id = EXCLUDED.bill_to_customer_id,
            published = EXCLUDED.published,
            creation_type = EXCLUDED.creation_type,
            status = EXCLUDED.status,
            payment_terms = EXCLUDED.payment_terms,
            customer_ref = EXCLUDED.customer_ref,
            freight_terms = EXCLUDED.freight_terms,
            exp_date = EXCLUDED.exp_date,
            revise_date = EXCLUDED.revise_date,
            accept_date = EXCLUDED.accept_date,
            blanket = EXCLUDED.blanket,
            duplicated_from = EXCLUDED.duplicated_from,
            balance_id = EXCLUDED.balance_id,
            job_id = EXCLUDED.job_id
        """,
        [(
            q["id"],
            q["quote_number"],
            q["entity_date"],
            q["sold_to_customer_id"],
            q["bill_to_customer_id"],
            q["published"],
            q["creation_type"],
            q["status"],
            q["payment_terms"],
            q["customer_ref"],
            q["freight_terms"],
            q["exp_date"],
            q["revise_date"],
            q["accept_date"],
            q["blanket"],
            q["duplicated_from"],
            q["balance_id"],
            q["created_by_id"],
            q["created_at"],
            q["job_id"],
        ) for q in quotes],
    )

    logger.info(f"Migrated {len(quotes)} quotes")
    return len(quotes)


async def migrate_quote_details(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quote details from v5 (crm.quote_details) to v6 (pycrm.quote_details)."""
    logger.info("Starting quote detail migration...")

    details = await source.fetch("""
        SELECT
            qd.id,
            qd.quote_id,
            qd.item_number,
            COALESCE(qd.quantity, 0) as quantity,
            COALESCE(qd.unit_price, 0) as unit_price,
            COALESCE(qd.subtotal, 0) as subtotal,
            COALESCE(qd.total, 0) as total,
            COALESCE(qd.commission, 0) as total_line_commission,
            COALESCE(qd.commission_rate, 0) as commission_rate,
            COALESCE(qd.commission, 0) as commission,
            COALESCE(qd.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(qd.commission_discount, 0) as commission_discount,
            COALESCE(qd.discount_rate, 0) as discount_rate,
            COALESCE(qd.discount, 0) as discount,
            qd.product_id,
            qd.factory_id,
            qd.end_user_id,
            qd.lead_time,
            qd.note,
            qd.status + 1 AS status,
            qd.lost_reason_id,
            CASE
                WHEN qd.uom_multiply AND qd.uom_multiply_by > 0 THEN qd.uom_multiply_by
                ELSE NULL
            END AS division_factor
        FROM crm.quote_details qd
        LEFT JOIN crm.quotes q ON q.id = qd.quote_id
        WHERE
            q.sold_to_customer_id IS NOT NULL
    """)

    if not details:
        logger.info("No quote details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.quote_details (
            id, quote_id, item_number, quantity, unit_price, subtotal, total,
            total_line_commission, commission_rate, commission, commission_discount_rate,
            commission_discount, discount_rate, discount, product_id, product_name_adhoc,
            product_description_adhoc, factory_id, end_user_id, lead_time, note,
            status, lost_reason_id, uom_id, division_factor, order_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NULL, NULL, $16, $17, $18, $19, $20, $21, NULL, $22, NULL)
        ON CONFLICT (id) DO UPDATE SET
            quote_id = EXCLUDED.quote_id,
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
            product_id = EXCLUDED.product_id,
            factory_id = EXCLUDED.factory_id,
            end_user_id = EXCLUDED.end_user_id,
            lead_time = EXCLUDED.lead_time,
            note = EXCLUDED.note,
            status = EXCLUDED.status,
            lost_reason_id = EXCLUDED.lost_reason_id,
            division_factor = EXCLUDED.division_factor
        """,
        [(
            d["id"],
            d["quote_id"],
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
            d["product_id"],
            d["factory_id"],
            d["end_user_id"],
            d["lead_time"],
            d["note"],
            d["status"],
            d["lost_reason_id"],
            d["division_factor"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} quote details")
    return len(details)


async def migrate_quote_split_rates(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quote split rates from v5 (crm.quote_split_rates) to v6 (pycrm.quote_split_rates)."""
    logger.info("Starting quote split rate migration...")

    split_rates = await source.fetch("""
        SELECT
            qsr.id,
            qsr.quote_detail_id,
            qsr.user_id,
            COALESCE(qsr.split_rate, 0) as split_rate,
            COALESCE(qsr."position", 0) as position,
            COALESCE(qsr.entry_date, now()) as created_at
        FROM crm.quote_split_rates qsr
        JOIN crm.quote_details qd ON qd.id = qsr.quote_detail_id
        JOIN crm.quotes q ON q.id = qd.quote_id
        WHERE
            q.sold_to_customer_id IS NOT NULL
    """)

    if not split_rates:
        logger.info("No quote split rates to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.quote_split_rates (
            id, quote_detail_id, user_id, split_rate, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            quote_detail_id = EXCLUDED.quote_detail_id,
            user_id = EXCLUDED.user_id,
            split_rate = EXCLUDED.split_rate,
            "position" = EXCLUDED."position"
        """,
        [(
            sr["id"],
            sr["quote_detail_id"],
            sr["user_id"],
            sr["split_rate"],
            sr["position"],
            sr["created_at"],
        ) for sr in split_rates],
    )

    logger.info(f"Migrated {len(split_rates)} quote split rates")
    return len(split_rates)


async def migrate_quote_inside_reps(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quote inside reps from v5 (crm.quote_inside_reps) to v6 (pycrm.quote_inside_reps)."""
    logger.info("Starting quote inside rep migration...")

    inside_reps = await source.fetch("""
        SELECT
            qir.id,
            qd.id AS quote_detail_id,
            qir.user_id,
            COALESCE(qir.entry_date, now()) as created_at
        FROM crm.quote_inside_reps qir
        LEFT JOIN crm.quote_details qd ON qd.quote_id = qir.quote_id AND qd.item_number = 1
        JOIN crm.quotes q ON q.id = qd.quote_id
        WHERE
            q.sold_to_customer_id IS NOT NULL
    """)

    if not inside_reps:
        logger.info("No quote inside reps to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.quote_inside_reps (
            id, quote_detail_id, user_id, split_rate, "position", created_at
        ) VALUES ($1, $2, $3, 100, 0, $4)
        ON CONFLICT (id) DO UPDATE SET
            quote_detail_id = EXCLUDED.quote_detail_id,
            user_id = EXCLUDED.user_id
        """,
        [(
            ir["id"],
            ir["quote_detail_id"],
            ir["user_id"],
            ir["created_at"],
        ) for ir in inside_reps],
    )

    logger.info(f"Migrated {len(inside_reps)} quote inside reps")
    return len(inside_reps)


async def run_migration(config: MigrationConfig) -> dict[str, int]:
    """Run full migration from v5 to v6."""
    logger.info("Connecting to databases...")

    # Connection settings to prevent timeouts during long migrations
    connection_timeout = 60
    command_timeout = 600.0  # 10 minutes for individual commands

    # Server settings to keep connection alive
    server_settings = {
        "statement_timeout": "0",  # No statement timeout
        "idle_in_transaction_session_timeout": "0",  # No idle timeout
    }

    source = await asyncpg.connect(
        config.source_dsn,
        timeout=connection_timeout,
        command_timeout=command_timeout,
        server_settings=server_settings,
    )
    dest = await asyncpg.connect(
        config.dest_dsn,
        timeout=connection_timeout,
        command_timeout=command_timeout,
        server_settings=server_settings,
    )

    results: dict[str, int] = {}

    try:
        # Order matters due to foreign key dependencies
        # results["users"] = await migrate_users(source, dest)
        # results["folders"] = await migrate_folders(source, dest)
        # results["files"] = await migrate_files(source, dest)
        # results["customers"] = await migrate_customers(source, dest)
        # results["factories"] = await migrate_factories(source, dest)
        # results["product_uoms"] = await migrate_product_uoms(source, dest)
        # results["product_categories"] = await migrate_product_categories(source, dest)
        # results["products"] = await migrate_products(source, dest)
        # results["product_cpns"] = await migrate_product_cpns(source, dest)
        # results["job_statuses"] = await migrate_job_statuses(source, dest)
        # results["jobs"] = await migrate_jobs(source, dest)
        # results["quote_balances"] = await migrate_quote_balances(source, dest)
        # results["quote_lost_reasons"] = await migrate_quote_lost_reasons(source, dest)
        # results["quotes"] = await migrate_quotes(source, dest)
        # results["quote_details"] = await migrate_quote_details(source, dest)
        # results["quote_split_rates"] = await migrate_quote_split_rates(source, dest)
        # results["quote_inside_reps"] = await migrate_quote_inside_reps(source, dest)
        # results["customer_factory_sales_reps"] = await migrate_customer_factory_sales_reps(source, dest)
        # results["inside_customer_split_rates"] = await migrate_inside_customer_split_rates(source, dest)
        # results["customer_split_rates"] = await migrate_customer_split_rates(source, dest)
        # results["factory_split_rates"] = await migrate_factory_split_rates(source, dest)
        # results["addresses"] = await migrate_addresses(source, dest)
        # results["contacts"] = await migrate_contacts(source, dest)
        # results["contact_links"] = await migrate_contact_links(source, dest)
        # results["notes"] = await migrate_notes(source, dest)
        # results["tasks"] = await migrate_tasks(source, dest)
        # results["link_relations"] = await migrate_link_relations(source, dest)
        # results["companies"] = await migrate_companies(source, dest)
        # results["order_balances"] = await migrate_order_balances(source, dest)
        # results["orders"] = await migrate_orders(source, dest)
        # results["order_details"] = await migrate_order_details(source, dest)
        # results["order_inside_reps"] = await migrate_order_inside_reps(source, dest)
        # results["order_split_rates"] = await migrate_order_split_rates(source, dest)
        # results["order_acknowledgements"] = await migrate_order_acknowledgements(source, dest)
        # results["invoice_balances"] = await migrate_invoice_balances(source, dest)
        # results["invoices"] = await migrate_invoices(source, dest)
        # results["invoice_details"] = await migrate_invoice_details(source, dest)
        # results["invoice_split_rates"] = await migrate_invoice_split_rates(source, dest)
        results["credit_balances"] = await migrate_credit_balances(source, dest)
        results["credits"] = await migrate_credits(source, dest)
        results["credit_details"] = await migrate_credit_details(source, dest)
        results["credit_split_rates"] = await migrate_credit_split_rates(source, dest)
        results["adjustments"] = await migrate_adjustments(source, dest)
        results["adjustment_split_rates"] = await migrate_adjustment_split_rates(source, dest)
        results["checks"] = await migrate_checks(source, dest)
        results["check_details"] = await migrate_check_details(source, dest)

        # AI tables (same schema in both source and dest)
        for table in AI_TABLES:
            results[table] = await migrate_ai_table(source, dest, table)

        logger.info("Migration completed successfully!")
        logger.info(f"Results: {results}")

    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        raise
    finally:
        await source.close()
        await dest.close()

    return results


async def run_migration_for_tenant(
    source_tenant: str,
    source_base_url: str,
    dest_tenant: str,
    dest_base_url: str,
) -> dict[str, int]:
    """Run migration for a specific tenant."""
    config = MigrationConfig(
        source_dsn=f"{source_base_url}/{source_tenant}",
        dest_dsn=f"{dest_base_url}/{dest_tenant}",
    )
    logger.info(f"Running migration for tenant: {source_tenant} to {dest_tenant}")
    return await run_migration(config)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Migrate data from v5 to v6")
    _ = parser.add_argument(
        "--source-tenant",
        required=True,
        help="Source database tenant name",
    )
    _ = parser.add_argument(
        "--source-url",
        default=os.environ.get("V5_DATABASE_URL"),
        help="Source database base URL (without tenant)",
    )
    _ = parser.add_argument(
        "--dest-tenant",
        required=True,
        help="Destination database tenant name",
    )
    _ = parser.add_argument(
        "--dest-url",
        default=os.environ.get("V6_DATABASE_URL"),
        help="Destination database base URL (without tenant)",
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be migrated without making changes",
    )
    args = parser.parse_args()

    if not args.source_url or not args.dest_url:
        parser.error("--source-url and --dest-url are required (or set V5_DATABASE_URL and V6_DATABASE_URL)")

    _ = asyncio.run(run_migration_for_tenant(
        source_tenant=args.source_tenant,
        dest_tenant=args.dest_tenant,
        source_base_url=args.source_url,
        dest_base_url=args.dest_url,
    ))
