import asyncio
import logging
import uuid
from dataclasses import dataclass

import asyncpg

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class MigrationConfig:
    source_dsn: str
    dest_dsn: str
    default_user_id: uuid.UUID
    batch_size: int = 500


def map_creation_type(value: str | None) -> int:
    """Map v4 string creation_type to v6 IntEnum value.

    v6 CreationType values:
        MANUAL = 0
        IMPORT = 1
        API = 2
        DUPLICATION = 3
    """
    if value is None:
        return 0  # MANUAL
    value_lower = value.lower()
    if value_lower == "manual":
        return 0
    if value_lower in ("spreadsheet", "import"):
        return 1
    if value_lower == "api":
        return 2
    if value_lower == "duplication":
        return 3
    return 0  # Default to MANUAL


def map_freight_discount_type(value: str | None) -> int:
    """Map v4 string freight_discount_type to v6 IntEnum value.

    v6 FreightDiscountTypeEnum values:
        ADD = 0
        ALLOWED = 1
    """
    if value is None or value == "":
        return 0  # ADD (default)
    value_lower = value.lower()
    if value_lower == "allowed":
        return 1
    return 0  # Default to ADD


def map_order_status(v4_status: int | None) -> int:
    """Map v4 order_status id to v6 OrderStatus IntEnum value.

    v4 order_status:
        1 = Open
        2 = Partial Shipped
        3 = Shipped Complete
        5 = Needs Reconciling
        6 = Paid - Matched
        7 = Over Shipped
        8 = Cancelled

    v6 OrderStatus (IntEnum with auto() starting at 1):
        1 = OPEN
        2 = PARTIAL_SHIPPED
        3 = SHIPPED_COMPLETE
        4 = CANCELLED
        5 = OVER_SHIPPED
        6 = PARTIAL_CANCELLED
        7 = OVER_CANCELLED
    """
    if v4_status is None:
        return 1  # OPEN
    mapping = {
        1: 1,  # Open -> OPEN
        2: 2,  # Partial Shipped -> PARTIAL_SHIPPED
        3: 3,  # Shipped Complete -> SHIPPED_COMPLETE
        5: 1,  # Needs Reconciling -> OPEN (no direct equivalent)
        6: 3,  # Paid - Matched -> SHIPPED_COMPLETE (closest match)
        7: 5,  # Over Shipped -> OVER_SHIPPED
        8: 4,  # Cancelled -> CANCELLED
    }
    return mapping.get(v4_status, 1)  # Default to OPEN


async def migrate_users(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate users from v4 (public.users) to v6 (pyuser.users)."""
    logger.info("Starting user migration...")

    users = await source.fetch("""
        SELECT
            u.id,
            u.username,
            u.firstname as first_name,
            u.lastname as last_name,
            u.email,
            gen_random_uuid()::text as auth_provider_id,
            CASE
                WHEN u.keycloak_role = 1 THEN 1
                WHEN u.keycloak_role = 2 THEN 2
                WHEN u.keycloak_role = 3 THEN 3
                ELSE 4
            END AS role,
            COALESCE(u.status, true) as enabled,
            COALESCE(u.is_inside, false) as inside,
            COALESCE(u.is_outside, false) as outside,
            now() as created_at
        FROM public.users u
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


async def migrate_customers(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    default_user_id: uuid.UUID,
) -> int:
    """Migrate customers from v4 (public.customers) to v6 (pycore.customers)."""
    logger.info("Starting customer migration...")

    # First, get customers without parents (using uuid field as id)
    parent_customers = await source.fetch("""
        SELECT
            c.uuid as id,
            c.company_name,
            COALESCE(c.status, true) as published,
            COALESCE(c.is_parent, false) as is_parent,
            c.contact_email,
            c.contact_number,
            c.created_by as created_by_id,
            COALESCE(c.create_date, now()) as created_at
        FROM public.customers c
        WHERE c.parent_id IS NULL
    """)

    # Get valid user IDs from destination to check created_by references
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

    if parent_customers:
        await dest.executemany(
            """
            INSERT INTO pycore.customers (
                id, company_name, parent_id, published, is_parent,
                contact_email, contact_number, created_by_id, created_at
            ) VALUES ($1, $2, NULL, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                published = EXCLUDED.published,
                is_parent = EXCLUDED.is_parent,
                contact_email = EXCLUDED.contact_email,
                contact_number = EXCLUDED.contact_number
            """,
            [(
                c["id"],
                c["company_name"],
                c["published"],
                c["is_parent"],
                c["contact_email"],
                c["contact_number"],
                c["created_by_id"] if c["created_by_id"] in valid_user_ids else default_user_id,
                c["created_at"],
            ) for c in parent_customers],
        )

    # Then get and insert child customers (mapping parent_id integer to parent's uuid)
    child_customers = await source.fetch("""
        SELECT
            c.uuid as id,
            c.company_name,
            parent.uuid as parent_id,
            COALESCE(c.status, true) as published,
            COALESCE(c.is_parent, false) as is_parent,
            c.contact_email,
            c.contact_number,
            c.created_by as created_by_id,
            COALESCE(c.create_date, now()) as created_at
        FROM public.customers c
        JOIN public.customers parent ON c.parent_id = parent.customer_id
        WHERE c.parent_id IS NOT NULL
    """)

    if child_customers:
        await dest.executemany(
            """
            INSERT INTO pycore.customers (
                id, company_name, parent_id, published, is_parent,
                contact_email, contact_number, created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                parent_id = EXCLUDED.parent_id,
                published = EXCLUDED.published,
                is_parent = EXCLUDED.is_parent,
                contact_email = EXCLUDED.contact_email,
                contact_number = EXCLUDED.contact_number
            """,
            [(
                c["id"],
                c["company_name"],
                c["parent_id"],
                c["published"],
                c["is_parent"],
                c["contact_email"],
                c["contact_number"],
                c["created_by_id"] if c["created_by_id"] in valid_user_ids else default_user_id,
                c["created_at"],
            ) for c in child_customers],
        )

    total = len(parent_customers) + len(child_customers)
    logger.info(f"Migrated {total} customers ({len(parent_customers)} parents, {len(child_customers)} children)")
    return total


async def migrate_factories(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    default_user_id: uuid.UUID,
) -> int:
    """Migrate factories from v4 (public.factories) to v6 (pycore.factories)."""
    logger.info("Starting factory migration...")

    factories = await source.fetch(r"""
        SELECT
            f.uuid as id,
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
            COALESCE(f.base_commission, 0) as base_commission_rate,
            COALESCE(f.commission_discount, 0) as commission_discount_rate,
            COALESCE(f.overall_discount, 0) as overall_discount_rate,
            f.additional_information,
            f.freight_terms,
            f.external_payment_terms,
            COALESCE(f.status, true) as published,
            f.discount_type as freight_discount_type,
            f.creation_type,
            f.created_by as created_by_id,
            COALESCE(f.create_date, now()) as created_at
        FROM public.factories f
    """)

    if not factories:
        logger.info("No factories to migrate")
        return 0

    # Get valid user IDs from destination
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

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
            map_freight_discount_type(f["freight_discount_type"]),
            map_creation_type(f["creation_type"]),
            f["created_by_id"] if f["created_by_id"] in valid_user_ids else default_user_id,
            f["created_at"],
        ) for f in factories],
    )

    logger.info(f"Migrated {len(factories)} factories")
    return len(factories)


async def migrate_product_uoms(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate product UOMs from v4 (public.unit_of_measures) to v6 (pycore.product_uoms)."""
    logger.info("Starting product UOM migration...")

    uoms = await source.fetch("""
        SELECT
            u.uom_id as id,
            u.title,
            u.description,
            now() as created_at,
            CASE
                WHEN u.multiply AND u.multiply_by > 0 THEN u.multiply_by
                ELSE 1
            END AS division_factor
        FROM public.unit_of_measures u
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
            1,  # IMPORT (CreationType.IMPORT = 1)
            u["created_at"],
            u["division_factor"],
        ) for u in uoms],
    )

    logger.info(f"Migrated {len(uoms)} product UOMs")
    return len(uoms)


async def migrate_product_categories(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate product categories from v4 (public.product_categories) to v6 (pycore.product_categories)."""
    logger.info("Starting product category migration...")

    # Map integer factory_id to factory's uuid
    categories = await source.fetch("""
        SELECT
            pc.uuid as id,
            pc.title,
            COALESCE(pc.commission_rate, 0) as commission_rate,
            f.uuid as factory_id
        FROM public.product_categories pc
        JOIN public.factories f ON pc.factory_id = f.factory_id
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


async def migrate_products(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    default_user_id: uuid.UUID,
) -> int:
    """Migrate products from v4 (public.products) to v6 (pycore.products)."""
    logger.info("Starting product migration...")

    # Map integer factory_id to factory's uuid
    products = await source.fetch(r"""
        SELECT
            p.uuid as id,
            p.factory_part_number,
            COALESCE(p.unit_price, 0) as unit_price,
            COALESCE(p.commission_rate, 0) as default_commission_rate,
            f.uuid as factory_id,
            p.category_uuid as product_category_id,
            p.uom_id as product_uom_id,
            COALESCE(p.status, true) as published,
            COALESCE(p.approval_needed, false) as approval_needed,
            p.description,
            p.creation_type,
            COALESCE(p.create_date, now()) as created_at,
            p.created_by as created_by_id,
            p.ind_upc as upc,
            p.min_order_qty,
            CASE
                WHEN p.lead_time ~ '^\d+$' THEN p.lead_time::integer
                ELSE NULL
            END AS lead_time,
            p.discount_rate as unit_price_discount_rate,
            p.commission_discount_rate,
            CASE
                WHEN p.approval_date ~ '^\d{4}-\d{2}-\d{2}' THEN p.approval_date::date
                ELSE NULL
            END AS approval_date,
            p.approval_comments
        FROM public.products p
        LEFT JOIN public.factories f ON p.factory_id = f.factory_id
    """)

    if not products:
        logger.info("No products to migrate")
        return 0

    # Get valid user IDs from destination
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

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
            map_creation_type(p["creation_type"]),
            p["created_at"],
            p["created_by_id"] if p["created_by_id"] in valid_user_ids else default_user_id,
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
    """Migrate product CPNs from v4 (public.product_cpn) to v6 (pycore.product_cpns)."""
    logger.info("Starting product CPN migration...")

    # Map integer product_id and customer_id to their uuids
    cpns = await source.fetch("""
        SELECT
            cpn.uuid as id,
            cpn.customer_part_number,
            COALESCE(cpn.unit_price, 0) as unit_price,
            COALESCE(cpn.commission_rate, 0) as commission_rate,
            p.uuid as product_id,
            c.uuid as customer_id
        FROM public.product_cpn cpn
        JOIN public.products p ON cpn.product_id = p.product_id
        JOIN public.customers c ON cpn.customer_id = c.customer_id
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


async def migrate_customer_split_rates(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate customer split rates from v4 to v6."""
    logger.info("Starting customer split rate migration...")

    # Get list of migrated customer IDs from destination
    migrated_customers = await dest.fetch("SELECT id FROM pycore.customers")
    migrated_customer_ids = {row["id"] for row in migrated_customers}

    # Map integer customer_id to customer's uuid
    split_rates = await source.fetch("""
        SELECT
            csr.id,
            csr.user_id,
            c.uuid as customer_id,
            COALESCE(csr.split_rate, 0) as split_rate,
            1 as rep_type,
            0 as position,
            COALESCE(csr.create_date, now()) as created_at
        FROM public.default_outside_rep_customer_split csr
        JOIN public.customers c ON csr.customer_id = c.customer_id
    """)

    # Filter to only include split rates for customers that were migrated
    split_rates = [sr for sr in split_rates if sr["customer_id"] in migrated_customer_ids]

    if not split_rates:
        logger.info("No customer split rates to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.customer_split_rates (
            id, user_id, customer_id, split_rate, rep_type, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            customer_id = EXCLUDED.customer_id,
            split_rate = EXCLUDED.split_rate,
            rep_type = EXCLUDED.rep_type,
            "position" = EXCLUDED."position"
        """,
        [(
            sr["id"],
            sr["user_id"],
            sr["customer_id"],
            sr["split_rate"],
            sr["rep_type"],
            sr["position"],
            sr["created_at"],
        ) for sr in split_rates],
    )

    logger.info(f"Migrated {len(split_rates)} customer split rates")
    return len(split_rates)


async def migrate_customer_factory_sales_reps(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate customer factory sales reps from v4 to v6."""
    logger.info("Starting customer factory sales rep migration...")

    # Get list of migrated customer and factory IDs from destination
    migrated_customers = await dest.fetch("SELECT id FROM pycore.customers")
    migrated_customer_ids = {row["id"] for row in migrated_customers}
    migrated_factories = await dest.fetch("SELECT id FROM pycore.factories")
    migrated_factory_ids = {row["id"] for row in migrated_factories}

    # Join sales_rep_selection with default_outside_rep_split
    sales_reps = await source.fetch("""
        SELECT
            dors.id,
            c.uuid as customer_id,
            f.uuid as factory_id,
            dors.user_id,
            COALESCE(dors.split_rate, 0) as rate,
            0 as position,
            COALESCE(dors.create_date, now()) as created_at
        FROM public.default_outside_rep_split dors
        JOIN public.sales_rep_selection srs ON dors.selection_id = srs.id
        JOIN public.customers c ON srs.customer = c.customer_id
        JOIN public.factories f ON srs.factory = f.factory_id
        WHERE dors.user_id IS NOT NULL
    """)

    # Filter to only include sales reps for customers and factories that were migrated
    sales_reps = [
        sr for sr in sales_reps
        if sr["customer_id"] in migrated_customer_ids and sr["factory_id"] in migrated_factory_ids
    ]

    if not sales_reps:
        logger.info("No customer factory sales reps to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.customer_factory_sales_reps (
            id, customer_id, factory_id, user_id, rate, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            customer_id = EXCLUDED.customer_id,
            factory_id = EXCLUDED.factory_id,
            user_id = EXCLUDED.user_id,
            rate = EXCLUDED.rate,
            "position" = EXCLUDED."position"
        """,
        [(
            sr["id"],
            sr["customer_id"],
            sr["factory_id"],
            sr["user_id"],
            sr["rate"],
            sr["position"],
            sr["created_at"],
        ) for sr in sales_reps],
    )

    logger.info(f"Migrated {len(sales_reps)} customer factory sales reps")
    return len(sales_reps)


async def migrate_orders(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    default_user_id: uuid.UUID,
) -> int:
    """Migrate orders from v4 (public.orders) to v6 (pycommission.orders)."""
    logger.info("Starting order migration...")

    orders = await source.fetch("""
        SELECT
            o.uuid as id,
            gen_random_uuid() as balance_id,
            o.order_number,
            COALESCE(o.order_date, o.create_date) as entity_date,
            o.due_date,
            c.uuid as sold_to_customer_id,
            c.uuid as bill_to_customer_id,
            NOT COALESCE(o.draft, false) as published,
            o.creation_type,
            COALESCE(o.status, 1) as status,
            COALESCE(o.order_type, 0) + 1 as order_type,
            1 as header_status,
            f.uuid as factory_id,
            o.payment_terms as shipping_terms,
            o.freight_terms,
            o.pro_number as mark_number,
            o.ship_date,
            o.fact_so_number,
            o.created_by as created_by_id,
            COALESCE(o.create_date, now()) as created_at,
            COALESCE(o.quantity, 0) as quantity,
            COALESCE(o.order_balance, 0) as subtotal,
            COALESCE(o.order_amount, 0) as total,
            COALESCE(o.commission, 0) as commission,
            COALESCE(o.discount, 0) as discount,
            COALESCE(o.commission_rate, 0) as commission_rate,
            COALESCE(o.commission_discount, 0) as commission_discount,
            COALESCE(o.shipping_balance, 0) as shipping_balance
        FROM public.orders o
        JOIN public.customers c ON o.customer = c.customer_id
        JOIN public.factories f ON o.factory_id = f.factory_id
        WHERE c.uuid IS NOT NULL AND f.uuid IS NOT NULL
    """)

    if not orders:
        logger.info("No orders to migrate")
        return 0

    # First, create order_balances records
    await dest.executemany(
        """
        INSERT INTO pycommission.order_balances (
            id, quantity, subtotal, total, commission, discount, discount_rate,
            commission_rate, commission_discount, commission_discount_rate,
            shipping_balance, cancelled_balance, freight_charge_balance
        ) VALUES ($1, $2, $3, $4, $5, $6, 0, $7, $8, 0, $9, 0, 0)
        ON CONFLICT (id) DO NOTHING
        """,
        [(
            o["balance_id"],
            o["quantity"],
            o["subtotal"],
            o["total"],
            o["commission"],
            o["discount"],
            o["commission_rate"],
            o["commission_discount"],
            o["shipping_balance"],
        ) for o in orders],
    )

    # Get valid user IDs from destination
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

    await dest.executemany(
        """
        INSERT INTO pycommission.orders (
            id, order_number, entity_date, due_date, sold_to_customer_id, bill_to_customer_id,
            published, creation_type, status, order_type, header_status, factory_id,
            shipping_terms, freight_terms, mark_number, ship_date, projected_ship_date,
            fact_so_number, quote_id, balance_id, created_by_id, created_at, job_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NULL, $17, NULL, $18, $19, $20, NULL)
        ON CONFLICT (id) DO UPDATE SET
            order_number = EXCLUDED.order_number,
            entity_date = EXCLUDED.entity_date,
            due_date = EXCLUDED.due_date,
            sold_to_customer_id = EXCLUDED.sold_to_customer_id,
            bill_to_customer_id = EXCLUDED.bill_to_customer_id,
            published = EXCLUDED.published,
            creation_type = EXCLUDED.creation_type,
            status = EXCLUDED.status,
            order_type = EXCLUDED.order_type,
            header_status = EXCLUDED.header_status,
            factory_id = EXCLUDED.factory_id,
            shipping_terms = EXCLUDED.shipping_terms,
            freight_terms = EXCLUDED.freight_terms,
            mark_number = EXCLUDED.mark_number,
            ship_date = EXCLUDED.ship_date,
            fact_so_number = EXCLUDED.fact_so_number,
            balance_id = EXCLUDED.balance_id
        """,
        [(
            o["id"],
            o["order_number"],
            o["entity_date"],
            o["due_date"],
            o["sold_to_customer_id"],
            o["bill_to_customer_id"],
            o["published"],
            map_creation_type(o["creation_type"]),
            map_order_status(o["status"]),
            o["order_type"],
            o["header_status"],
            o["factory_id"],
            o["shipping_terms"],
            o["freight_terms"],
            o["mark_number"],
            o["ship_date"],
            o["fact_so_number"],
            o["balance_id"],
            o["created_by_id"] if o["created_by_id"] in valid_user_ids else default_user_id,
            o["created_at"],
        ) for o in orders],
    )

    logger.info(f"Migrated {len(orders)} orders")
    return len(orders)


async def migrate_order_details(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate order details from v4 to v6."""
    logger.info("Starting order detail migration...")

    details = await source.fetch("""
        SELECT
            gen_random_uuid() as id,
            o.uuid as order_id,
            COALESCE(od.item_number, 1) as item_number,
            COALESCE(od.quantity, 0) as quantity,
            COALESCE(od.unit_price, 0) as unit_price,
            COALESCE(od.quantity * od.unit_price, 0) as subtotal,
            COALESCE(od.total, 0) as total,
            COALESCE(od.commission, 0) as total_line_commission,
            COALESCE(od.commission_rate, 0) as commission_rate,
            COALESCE(od.commission, 0) as commission,
            COALESCE(od.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(od.commission_discount, 0) as commission_discount,
            COALESCE(od.discount_rate, 0) as discount_rate,
            COALESCE(od.discount, 0) as discount,
            p.uuid as product_id,
            eu.uuid as end_user_id,
            od.lead_time,
            COALESCE(od.status, 1) as status,
            COALESCE(od.shipping_balance, 0) as shipping_balance
        FROM public.order_details od
        JOIN public.orders o ON od.order_id = o.order_id
        JOIN public.customers c ON o.customer = c.customer_id
        JOIN public.factories f ON o.factory_id = f.factory_id
        LEFT JOIN public.products p ON od.product_id = p.product_id
        LEFT JOIN public.customers eu ON od.end_user = eu.customer_id
        WHERE c.uuid IS NOT NULL AND f.uuid IS NOT NULL
    """, timeout=600)

    if not details:
        logger.info("No order details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.order_details (
            id, order_id, item_number, quantity, unit_price, subtotal, total,
            total_line_commission, commission_rate, commission, commission_discount_rate,
            commission_discount, discount_rate, discount, division_factor, product_id,
            product_name_adhoc, product_description_adhoc, end_user_id,
            uom_id, lead_time, note, status, freight_charge, shipping_balance, cancelled_balance
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NULL, $15, NULL, NULL, $16, NULL, $17, NULL, $18, 0, $19, 0)
        """,
        [(
            d["id"],
            d["order_id"],
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
            d["end_user_id"],
            d["lead_time"],
            d["status"],
            d["shipping_balance"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} order details")
    return len(details)


async def migrate_quotes(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    default_user_id: uuid.UUID,
) -> int:
    """Migrate quotes from v4 (public.quotes) to v6 (pycrm.quotes)."""
    logger.info("Starting quote migration...")

    quotes = await source.fetch(r"""
        SELECT
            q.uuid as id,
            gen_random_uuid() as balance_id,
            q.quote_number,
            COALESCE(q.quote_date, q.create_date::date) as entity_date,
            c.uuid as sold_to_customer_id,
            c.uuid as bill_to_customer_id,
            NOT COALESCE(q.draft, false) as published,
            q.creation_type,
            COALESCE(q.status, 1) as status,
            q.payment_terms,
            q.customer_ref,
            q.freight_terms,
            CASE
                WHEN q.exp_date ~ '^\d{4}-\d{2}-\d{2}' THEN q.exp_date::date
                ELSE NULL
            END AS exp_date,
            CASE
                WHEN q.revise_date ~ '^\d{4}-\d{2}-\d{2}' THEN q.revise_date::date
                ELSE NULL
            END AS revise_date,
            CASE
                WHEN q.accept_date ~ '^\d{4}-\d{2}-\d{2}' THEN q.accept_date::date
                ELSE NULL
            END AS accept_date,
            COALESCE(q.blanket, false) as blanket,
            q.created_by as created_by_id,
            COALESCE(q.create_date, now()) as created_at,
            COALESCE(q.total_items, 0) as quantity,
            COALESCE(q.total, 0) as subtotal,
            COALESCE(q.total, 0) as total,
            COALESCE(q.commission, 0) as commission,
            COALESCE(q.discount, 0) as discount,
            COALESCE(q.commission_rate, 0) as commission_rate,
            COALESCE(q.commission_discount, 0) as commission_discount
        FROM public.quotes q
        JOIN public.customers c ON q.customer = c.customer_id
        WHERE c.uuid IS NOT NULL
    """)

    if not quotes:
        logger.info("No quotes to migrate")
        return 0

    # First, create quote_balances records
    await dest.executemany(
        """
        INSERT INTO pycrm.quote_balances (
            id, quantity, subtotal, total, commission, discount, discount_rate,
            commission_rate, commission_discount, commission_discount_rate
        ) VALUES ($1, $2, $3, $4, $5, $6, 0, $7, $8, 0)
        ON CONFLICT (id) DO NOTHING
        """,
        [(
            q["balance_id"],
            q["quantity"],
            q["subtotal"],
            q["total"],
            q["commission"],
            q["discount"],
            q["commission_rate"],
            q["commission_discount"],
        ) for q in quotes],
    )

    # Get valid user IDs from destination
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

    await dest.executemany(
        """
        INSERT INTO pycrm.quotes (
            id, quote_number, entity_date, sold_to_customer_id, bill_to_customer_id,
            published, creation_type, status, pipeline_stage, payment_terms,
            customer_ref, freight_terms, exp_date, revise_date, accept_date,
            blanket, duplicated_from, version_of, balance_id, created_by_id,
            created_at, job_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 0, $9, $10, $11, $12, $13, $14, $15, NULL, NULL, $16, $17, $18, NULL)
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
            balance_id = EXCLUDED.balance_id
        """,
        [(
            q["id"],
            q["quote_number"],
            q["entity_date"],
            q["sold_to_customer_id"],
            q["bill_to_customer_id"],
            q["published"],
            map_creation_type(q["creation_type"]),
            q["status"],
            q["payment_terms"],
            q["customer_ref"],
            q["freight_terms"],
            q["exp_date"],
            q["revise_date"],
            q["accept_date"],
            q["blanket"],
            q["balance_id"],
            q["created_by_id"] if q["created_by_id"] in valid_user_ids else default_user_id,
            q["created_at"],
        ) for q in quotes],
    )

    logger.info(f"Migrated {len(quotes)} quotes")
    return len(quotes)


async def migrate_quote_details(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quote details from v4 to v6."""
    logger.info("Starting quote detail migration...")

    details = await source.fetch("""
        SELECT
            gen_random_uuid() as id,
            q.uuid as quote_id,
            COALESCE(qd.item_number, 1) as item_number,
            COALESCE(qd.quantity, 0) as quantity,
            COALESCE(qd.unit_price, 0) as unit_price,
            COALESCE(qd.quantity * qd.unit_price, 0) as subtotal,
            COALESCE(qd.total, 0) as total,
            COALESCE(qd.commission, 0) as total_line_commission,
            COALESCE(qd.commission_rate, 0) as commission_rate,
            COALESCE(qd.commission, 0) as commission,
            COALESCE(qd.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(qd.commission_discount, 0) as commission_discount,
            COALESCE(qd.discount_rate, 0) as discount_rate,
            COALESCE(qd.discount, 0) as discount,
            p.uuid as product_id,
            f.uuid as factory_id,
            eu.uuid as end_user_id,
            qd.lead_time,
            COALESCE(qd.status, 1) as status,
            qd.lost_reason as lost_reason_id
        FROM public.quote_details qd
        JOIN public.quotes q ON qd.quote_id = q.quote_id
        JOIN public.customers c ON q.customer = c.customer_id
        LEFT JOIN public.products p ON qd.product_id = p.product_id
        LEFT JOIN public.factories f ON p.factory_id = f.factory_id
        LEFT JOIN public.customers eu ON qd.end_user = eu.customer_id
        WHERE c.uuid IS NOT NULL
    """, timeout=600)

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
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NULL, NULL, $16, $17, $18, NULL, $19, $20, NULL, NULL, NULL)
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
            d["status"],
            d["lost_reason_id"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} quote details")
    return len(details)


async def migrate_invoices(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    default_user_id: uuid.UUID,
) -> int:
    """Migrate invoices from v4 to v6."""
    logger.info("Starting invoice migration...")

    invoices = await source.fetch("""
        SELECT
            i.uuid as id,
            gen_random_uuid() as balance_id,
            i.invoice_number,
            COALESCE(i.invoice_date, i.create_date)::date as entity_date,
            i.due_date::date as due_date,
            COALESCE(i.status, 1) as status,
            NOT COALESCE(i.draft, false) as published,
            COALESCE(i.locked, false) as locked,
            i.creation_type,
            o.uuid as order_id,
            f.uuid as factory_id,
            i.created_by as created_by_id,
            COALESCE(i.create_date, now()) as created_at,
            COALESCE(i.invoice_amount, 0) as total,
            COALESCE(i.commission, 0) as commission,
            COALESCE(i.commission_rate, 0) as commission_rate,
            COALESCE(i.paid_amount, 0) as paid_balance
        FROM public.invoices i
        JOIN public.orders o ON i.order_id = o.order_id
        JOIN public.customers c ON o.customer = c.customer_id
        JOIN public.factories f ON i.factory_id = f.factory_id
        WHERE o.uuid IS NOT NULL AND f.uuid IS NOT NULL AND c.uuid IS NOT NULL
    """, timeout=600)

    if not invoices:
        logger.info("No invoices to migrate")
        return 0

    # First, create invoice_balances records
    await dest.executemany(
        """
        INSERT INTO pycommission.invoice_balances (
            id, quantity, subtotal, total, commission, discount, discount_rate,
            commission_rate, commission_discount, commission_discount_rate, paid_balance
        ) VALUES ($1, 0, $2, $2, $3, 0, 0, $4, 0, 0, $5)
        ON CONFLICT (id) DO NOTHING
        """,
        [(
            inv["balance_id"],
            inv["total"],
            inv["commission"],
            inv["commission_rate"],
            inv["paid_balance"],
        ) for inv in invoices],
    )

    # Get valid user IDs from destination
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

    await dest.executemany(
        """
        INSERT INTO pycommission.invoices (
            id, invoice_number, factory_id, order_id, entity_date, due_date,
            published, locked, creation_type, status, balance_id, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        ON CONFLICT (id) DO UPDATE SET
            invoice_number = EXCLUDED.invoice_number,
            factory_id = EXCLUDED.factory_id,
            order_id = EXCLUDED.order_id,
            entity_date = EXCLUDED.entity_date,
            due_date = EXCLUDED.due_date,
            published = EXCLUDED.published,
            locked = EXCLUDED.locked,
            creation_type = EXCLUDED.creation_type,
            status = EXCLUDED.status,
            balance_id = EXCLUDED.balance_id
        """,
        [(
            inv["id"],
            inv["invoice_number"],
            inv["factory_id"],
            inv["order_id"],
            inv["entity_date"],
            inv["due_date"],
            inv["published"],
            inv["locked"],
            map_creation_type(inv["creation_type"]),
            inv["status"],
            inv["balance_id"],
            inv["created_by_id"] if inv["created_by_id"] in valid_user_ids else default_user_id,
            inv["created_at"],
        ) for inv in invoices],
    )

    logger.info(f"Migrated {len(invoices)} invoices")
    return len(invoices)


async def migrate_invoice_details(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate invoice details from v4 to v6."""
    logger.info("Starting invoice detail migration...")

    details = await source.fetch("""
        SELECT
            gen_random_uuid() as id,
            inv.uuid as invoice_id,
            COALESCE(id.item_number, 1) as item_number,
            COALESCE(id.quantity_shipped, 0) as quantity,
            COALESCE(id.unit_price, 0) as unit_price,
            COALESCE(id.quantity_shipped * id.unit_price, 0) as subtotal,
            COALESCE(id.total, 0) as total,
            COALESCE(id.commission, 0) as total_line_commission,
            COALESCE(id.commission_rate, 0) as commission_rate,
            COALESCE(id.commission, 0) as commission,
            COALESCE(id.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(id.commission_discount, 0) as commission_discount,
            COALESCE(id.discount_rate, 0) as discount_rate,
            COALESCE(id.discount, 0) as discount,
            p.uuid as product_id,
            eu.uuid as end_user_id,
            COALESCE(id.status, 1) as status
        FROM public.invoice_details id
        JOIN public.invoices inv ON id.invoice_id = inv.invoice_id
        JOIN public.orders o ON inv.order_id = o.order_id
        JOIN public.customers c ON o.customer = c.customer_id
        JOIN public.factories f ON inv.factory_id = f.factory_id
        LEFT JOIN public.products p ON id.product_id = p.product_id
        LEFT JOIN public.customers eu ON id.end_user = eu.customer_id
        WHERE inv.uuid IS NOT NULL AND c.uuid IS NOT NULL AND f.uuid IS NOT NULL
    """, timeout=600)

    if not details:
        logger.info("No invoice details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.invoice_details (
            id, invoice_id, item_number, quantity, unit_price, subtotal, total,
            total_line_commission, commission_rate, commission, commission_discount_rate,
            commission_discount, discount_rate, discount, division_factor, product_id,
            product_name_adhoc, product_description_adhoc, uom_id, end_user_id,
            lead_time, note, status, invoiced_balance, order_detail_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NULL, $15, NULL, NULL, NULL, $16, NULL, NULL, $17, 0, NULL)
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
            d["product_id"],
            d["end_user_id"],
            d["status"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} invoice details")
    return len(details)


async def migrate_order_split_rates(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate order split rates from v4 order_sales_rep_split to v6 order_split_rates."""
    logger.info("Starting order split rate migration...")

    # Get the mapping of v4 order_detail_id to v6 order_detail uuid
    # We need to join through orders to get the mapping
    split_rates = await source.fetch("""
        SELECT
            osrs.id,
            osrs.user_id,
            od.order_detail_id as v4_order_detail_id,
            o.uuid as order_id,
            od.item_number,
            COALESCE(osrs.split_rate, 0) as split_rate,
            COALESCE(osrs.create_date, now()) as created_at
        FROM public.order_sales_rep_split osrs
        JOIN public.order_details od ON osrs.order_detail_id = od.order_detail_id
        JOIN public.orders o ON od.order_id = o.order_id
        JOIN public.customers c ON o.customer = c.customer_id
        JOIN public.factories f ON o.factory_id = f.factory_id
        WHERE osrs.user_id IS NOT NULL
          AND c.uuid IS NOT NULL
          AND f.uuid IS NOT NULL
          AND o.uuid IS NOT NULL
    """, timeout=600)

    if not split_rates:
        logger.info("No order split rates to migrate")
        return 0

    # Get order_detail IDs from destination by matching order_id + item_number
    order_detail_map = await dest.fetch("""
        SELECT id, order_id, item_number
        FROM pycommission.order_details
    """)
    detail_lookup = {(d["order_id"], d["item_number"]): d["id"] for d in order_detail_map}

    # Get valid user IDs
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

    # Build records with mapped order_detail_id
    records = []
    for sr in split_rates:
        order_detail_id = detail_lookup.get((sr["order_id"], sr["item_number"]))
        if order_detail_id and sr["user_id"] in valid_user_ids:
            records.append((
                sr["id"],
                order_detail_id,
                sr["user_id"],
                sr["split_rate"],
                0,  # position
                sr["created_at"],
            ))

    if not records:
        logger.info("No valid order split rates to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.order_split_rates (
            id, order_detail_id, user_id, split_rate, position, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            order_detail_id = EXCLUDED.order_detail_id,
            user_id = EXCLUDED.user_id,
            split_rate = EXCLUDED.split_rate,
            position = EXCLUDED.position
        """,
        records,
    )

    logger.info(f"Migrated {len(records)} order split rates")
    return len(records)


async def migrate_quote_split_rates(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quote split rates from v4 quote_sales_rep_split to v6 quote_split_rates."""
    logger.info("Starting quote split rate migration...")

    split_rates = await source.fetch("""
        SELECT
            qsrs.id,
            qsrs.user_id,
            qd.quote_detail_id as v4_quote_detail_id,
            q.uuid as quote_id,
            qd.item_number,
            COALESCE(qsrs.split_rate, 0) as split_rate,
            COALESCE(qsrs.create_date, now()) as created_at
        FROM public.quote_sales_rep_split qsrs
        JOIN public.quote_details qd ON qsrs.quote_detail_id = qd.quote_detail_id
        JOIN public.quotes q ON qd.quote_id = q.quote_id
        JOIN public.customers c ON q.customer = c.customer_id
        WHERE qsrs.user_id IS NOT NULL
          AND c.uuid IS NOT NULL
          AND q.uuid IS NOT NULL
    """, timeout=600)

    if not split_rates:
        logger.info("No quote split rates to migrate")
        return 0

    # Get quote_detail IDs from destination by matching quote_id + item_number
    quote_detail_map = await dest.fetch("""
        SELECT id, quote_id, item_number
        FROM pycrm.quote_details
    """)
    detail_lookup = {(d["quote_id"], d["item_number"]): d["id"] for d in quote_detail_map}

    # Get valid user IDs
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

    # Build records with mapped quote_detail_id
    records = []
    for sr in split_rates:
        quote_detail_id = detail_lookup.get((sr["quote_id"], sr["item_number"]))
        if quote_detail_id and sr["user_id"] in valid_user_ids:
            records.append((
                sr["id"],
                quote_detail_id,
                sr["user_id"],
                sr["split_rate"],
                0,  # position
                sr["created_at"],
            ))

    if not records:
        logger.info("No valid quote split rates to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.quote_split_rates (
            id, quote_detail_id, user_id, split_rate, position, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            quote_detail_id = EXCLUDED.quote_detail_id,
            user_id = EXCLUDED.user_id,
            split_rate = EXCLUDED.split_rate,
            position = EXCLUDED.position
        """,
        records,
    )

    logger.info(f"Migrated {len(records)} quote split rates")
    return len(records)


async def migrate_invoice_split_rates(dest: asyncpg.Connection) -> int:
    """Create invoice split rates by inheriting from order split rates."""
    logger.info("Starting invoice split rate migration (inheriting from orders)...")

    # Get invoice details and their related order details
    # Then copy the order split rates to invoice split rates
    invoice_details = await dest.fetch("""
        SELECT
            id.id as invoice_detail_id,
            id.order_detail_id
        FROM pycommission.invoice_details id
        WHERE id.order_detail_id IS NOT NULL
    """)

    if not invoice_details:
        logger.info("No invoice details with order_detail_id to migrate split rates")
        return 0

    # Get order split rates
    order_split_rates = await dest.fetch("""
        SELECT
            order_detail_id,
            user_id,
            split_rate,
            position
        FROM pycommission.order_split_rates
    """)

    # Build lookup by order_detail_id
    order_splits_lookup: dict[uuid.UUID, list[tuple]] = {}
    for osr in order_split_rates:
        if osr["order_detail_id"] not in order_splits_lookup:
            order_splits_lookup[osr["order_detail_id"]] = []
        order_splits_lookup[osr["order_detail_id"]].append((
            osr["user_id"],
            osr["split_rate"],
            osr["position"],
        ))

    # Build invoice split rate records
    records = []
    for inv_detail in invoice_details:
        order_detail_id = inv_detail["order_detail_id"]
        if order_detail_id in order_splits_lookup:
            for user_id, split_rate, position in order_splits_lookup[order_detail_id]:
                records.append((
                    uuid.uuid4(),  # new id
                    inv_detail["invoice_detail_id"],
                    user_id,
                    split_rate,
                    position,
                ))

    if not records:
        logger.info("No invoice split rates to create from orders")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.invoice_split_rates (
            id, invoice_detail_id, user_id, split_rate, position, created_at
        ) VALUES ($1, $2, $3, $4, $5, now())
        ON CONFLICT (id) DO NOTHING
        """,
        records,
    )

    logger.info(f"Created {len(records)} invoice split rates from order split rates")
    return len(records)


async def migrate_checks(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    default_user_id: uuid.UUID,
) -> int:
    """Migrate checks from v4 to v6."""
    logger.info("Starting check migration...")

    checks = await source.fetch(r"""
        SELECT
            c.uuid as id,
            c.check_number,
            COALESCE(c.check_date, c.create_date::date) as entity_date,
            CASE
                WHEN c.post_date ~ '^\d{4}-\d{2}-\d{2}' THEN c.post_date::date
                ELSE NULL
            END AS post_date,
            CASE
                WHEN c.commission_month ~ '^\d{4}-\d{2}-\d{2}' THEN c.commission_month::date
                ELSE NULL
            END AS commission_month,
            COALESCE(c.commission_amount, 0) as entered_commission_amount,
            f.uuid as factory_id,
            1 as status,
            c.creation_type,
            c.created_by as created_by_id,
            COALESCE(c.create_date, now()) as created_at
        FROM public.checks c
        JOIN public.factories f ON c.factory = f.factory_id
        WHERE f.uuid IS NOT NULL
    """, timeout=600)

    if not checks:
        logger.info("No checks to migrate")
        return 0

    # Get valid user IDs from destination
    valid_users = await dest.fetch("SELECT id FROM pyuser.users")
    valid_user_ids = {u["id"] for u in valid_users}

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
            map_creation_type(c["creation_type"]),
            c["created_by_id"] if c["created_by_id"] in valid_user_ids else default_user_id,
            c["created_at"],
        ) for c in checks],
    )

    logger.info(f"Migrated {len(checks)} checks")
    return len(checks)


async def run_migration(config: MigrationConfig) -> dict[str, int]:
    """Run full migration from v4 to v6."""
    logger.info("Connecting to databases...")

    connection_timeout = 60
    command_timeout = 600.0

    server_settings = {
        "statement_timeout": "0",
        "idle_in_transaction_session_timeout": "0",
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
        default_user_id = config.default_user_id
        results["users"] = await migrate_users(source, dest)
        results["customers"] = await migrate_customers(source, dest, default_user_id)
        results["factories"] = await migrate_factories(source, dest, default_user_id)
        results["product_uoms"] = await migrate_product_uoms(source, dest)
        results["product_categories"] = await migrate_product_categories(source, dest)
        results["products"] = await migrate_products(source, dest, default_user_id)
        results["product_cpns"] = await migrate_product_cpns(source, dest)
        results["customer_split_rates"] = await migrate_customer_split_rates(source, dest)
        results["customer_factory_sales_reps"] = await migrate_customer_factory_sales_reps(source, dest)
        results["orders"] = await migrate_orders(source, dest, default_user_id)
        results["order_details"] = await migrate_order_details(source, dest)
        results["order_split_rates"] = await migrate_order_split_rates(source, dest)
        results["quotes"] = await migrate_quotes(source, dest, default_user_id)
        results["quote_details"] = await migrate_quote_details(source, dest)
        results["quote_split_rates"] = await migrate_quote_split_rates(source, dest)
        results["invoices"] = await migrate_invoices(source, dest, default_user_id)
        results["invoice_details"] = await migrate_invoice_details(source, dest)
        results["invoice_split_rates"] = await migrate_invoice_split_rates(dest)
        results["checks"] = await migrate_checks(source, dest, default_user_id)

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
    default_user_id: uuid.UUID,
) -> dict[str, int]:
    """Run migration for a specific tenant."""
    config = MigrationConfig(
        source_dsn=f"{source_base_url}/{source_tenant}",
        dest_dsn=f"{dest_base_url}/{dest_tenant}",
        default_user_id=default_user_id,
    )
    logger.info(f"Running migration for tenant: {source_tenant} to {dest_tenant}")
    return await run_migration(config)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Migrate data from v4 to v6")
    _ = parser.add_argument(
        "--source-tenant",
        required=True,
        help="Source database tenant name",
    )
    _ = parser.add_argument(
        "--source-url",
        default=os.environ.get("V4_DATABASE_URL"),
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
    _ = parser.add_argument(
        "--default-user-id",
        required=True,
        help="Default user UUID to use when created_by references a non-existent user",
    )
    args = parser.parse_args()

    if not args.source_url or not args.dest_url:
        parser.error("--source-url and --dest-url are required (or set V4_DATABASE_URL and V6_DATABASE_URL)")

    _ = asyncio.run(run_migration_for_tenant(
        source_tenant=args.source_tenant,
        dest_tenant=args.dest_tenant,
        source_base_url=args.source_url,
        dest_base_url=args.dest_url,
        default_user_id=uuid.UUID(args.default_user_id),
    ))
