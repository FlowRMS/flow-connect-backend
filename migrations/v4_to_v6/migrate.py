import asyncio
import logging
from dataclasses import dataclass

import asyncpg

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class MigrationConfig:
    source_dsn: str
    dest_dsn: str
    batch_size: int = 500


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
            NULL as auth_provider_id,
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


async def migrate_customers(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate customers from v4 (public.customers) to v6 (pycore.customers)."""
    logger.info("Starting customer migration...")

    # First, get customers without parents (using uuid field as id)
    parent_customers = await source.fetch("""
        SELECT
            c.uuid as id,
            c.company_name,
            COALESCE(c.status, true) as published,
            COALESCE(c.is_parent, false) as is_parent,
            c.created_by as created_by_id,
            COALESCE(c.create_date, now()) as created_at
        FROM public.customers c
        WHERE c.parent_id IS NULL
    """)

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

    # Then get and insert child customers (mapping parent_id integer to parent's uuid)
    child_customers = await source.fetch("""
        SELECT
            c.uuid as id,
            c.company_name,
            parent.uuid as parent_id,
            COALESCE(c.status, true) as published,
            COALESCE(c.is_parent, false) as is_parent,
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
    """Migrate product UOMs from v4 (public.unit_of_measures) to v6 (pycore.product_uoms)."""
    logger.info("Starting product UOM migration...")

    uoms = await source.fetch("""
        SELECT
            u.uom_id as id,
            u.title,
            u.description,
            'migration' as creation_type,
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
            u["creation_type"],
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


async def migrate_products(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
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
            p.approval_date,
            p.approval_comments
        FROM public.products p
        LEFT JOIN public.factories f ON p.factory_id = f.factory_id
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

    # Join sales_rep_selection with default_outside_rep_split
    sales_reps = await source.fetch("""
        SELECT
            dors.id,
            c.uuid as customer_id,
            f.uuid as factory_id,
            dors.user_id,
            COALESCE(dors.split_rate, 0) as split_rate,
            1 as rep_type,
            0 as position,
            COALESCE(dors.create_date, now()) as created_at
        FROM public.default_outside_rep_split dors
        JOIN public.sales_rep_selection srs ON dors.selection_id = srs.id
        JOIN public.customers c ON srs.customer = c.customer_id
        JOIN public.factories f ON srs.factory = f.factory_id
        WHERE dors.user_id IS NOT NULL
    """)

    if not sales_reps:
        logger.info("No customer factory sales reps to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.customer_factory_sales_reps (
            id, customer_id, factory_id, user_id, split_rate, rep_type, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (id) DO UPDATE SET
            customer_id = EXCLUDED.customer_id,
            factory_id = EXCLUDED.factory_id,
            user_id = EXCLUDED.user_id,
            split_rate = EXCLUDED.split_rate,
            rep_type = EXCLUDED.rep_type,
            "position" = EXCLUDED."position"
        """,
        [(
            sr["id"],
            sr["customer_id"],
            sr["factory_id"],
            sr["user_id"],
            sr["split_rate"],
            sr["rep_type"],
            sr["position"],
            sr["created_at"],
        ) for sr in sales_reps],
    )

    logger.info(f"Migrated {len(sales_reps)} customer factory sales reps")
    return len(sales_reps)


async def migrate_orders(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate orders from v4 (public.orders) to v6 (pycommission.orders)."""
    logger.info("Starting order migration...")

    orders = await source.fetch("""
        SELECT
            o.uuid as id,
            o.order_number,
            COALESCE(o.order_date, o.create_date) as entity_date,
            o.due_date,
            c.uuid as sold_to_customer_id,
            c.uuid as bill_to_customer_id,
            NOT COALESCE(o.draft, false) as published,
            o.creation_type,
            o.status,
            o.order_type,
            1 as header_status,
            f.uuid as factory_id,
            o.payment_terms as shipping_terms,
            o.freight_terms,
            o.pro_number as mark_number,
            o.ship_date,
            o.fact_so_number,
            o.created_by as created_by_id,
            COALESCE(o.create_date, now()) as created_at
        FROM public.orders o
        LEFT JOIN public.customers c ON o.customer = c.customer_id
        LEFT JOIN public.factories f ON o.factory_id = f.factory_id
    """)

    if not orders:
        logger.info("No orders to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.orders (
            id, order_number, entity_date, due_date, sold_to_customer_id, bill_to_customer_id,
            published, creation_type, status, order_type, header_status, factory_id,
            shipping_terms, freight_terms, mark_number, ship_date, projected_ship_date,
            fact_so_number, quote_id, balance_id, created_by_id, created_at, job_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NULL, $17, NULL, NULL, $18, $19, NULL)
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
            fact_so_number = EXCLUDED.fact_so_number
        """,
        [(
            o["id"],
            o["order_number"],
            o["entity_date"],
            o["due_date"],
            o["sold_to_customer_id"],
            o["bill_to_customer_id"],
            o["published"],
            o["creation_type"],
            o["status"],
            o["order_type"],
            o["header_status"],
            o["factory_id"],
            o["shipping_terms"],
            o["freight_terms"],
            o["mark_number"],
            o["ship_date"],
            o["fact_so_number"],
            o["created_by_id"],
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
            od.item_number,
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
            f.uuid as factory_id,
            eu.uuid as end_user_id,
            od.lead_time,
            od.status,
            COALESCE(od.shipping_balance, 0) as shipping_balance
        FROM public.order_details od
        JOIN public.orders o ON od.order_id = o.order_id
        LEFT JOIN public.products p ON od.product_id = p.product_id
        LEFT JOIN public.factories f ON o.factory_id = f.factory_id
        LEFT JOIN public.customers eu ON od.end_user = eu.customer_id
    """)

    if not details:
        logger.info("No order details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.order_details (
            id, order_id, item_number, quantity, unit_price, subtotal, total,
            total_line_commission, commission_rate, commission, commission_discount_rate,
            commission_discount, discount_rate, discount, division_factor, product_id,
            product_name_adhoc, product_description_adhoc, factory_id, end_user_id,
            uom_id, lead_time, note, status, freight_charge, shipping_balance, cancelled_balance
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NULL, $15, NULL, NULL, $16, $17, NULL, $18, NULL, $19, 0, $20, 0)
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
            d["factory_id"],
            d["end_user_id"],
            d["lead_time"],
            d["status"],
            d["shipping_balance"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} order details")
    return len(details)


async def migrate_quotes(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate quotes from v4 (public.quotes) to v6 (pycrm.quotes)."""
    logger.info("Starting quote migration...")

    quotes = await source.fetch("""
        SELECT
            q.uuid as id,
            q.quote_number,
            COALESCE(q.quote_date, q.create_date) as entity_date,
            c.uuid as sold_to_customer_id,
            c.uuid as bill_to_customer_id,
            NOT COALESCE(q.draft, false) as published,
            q.creation_type,
            q.status,
            q.payment_terms,
            q.customer_ref,
            q.freight_terms,
            q.exp_date,
            q.revise_date,
            q.accept_date,
            COALESCE(q.blanket, false) as blanket,
            q.created_by as created_by_id,
            COALESCE(q.create_date, now()) as created_at
        FROM public.quotes q
        LEFT JOIN public.customers c ON q.customer = c.customer_id
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
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 0, $9, $10, $11, $12, $13, $14, $15, NULL, NULL, NULL, $16, $17, NULL)
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
            blanket = EXCLUDED.blanket
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
            q["created_by_id"],
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
            qd.item_number,
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
            qd.status,
            qd.lost_reason as lost_reason_id
        FROM public.quote_details qd
        JOIN public.quotes q ON qd.quote_id = q.quote_id
        LEFT JOIN public.products p ON qd.product_id = p.product_id
        LEFT JOIN public.factories f ON p.factory_id = f.factory_id
        LEFT JOIN public.customers eu ON qd.end_user = eu.customer_id
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


async def migrate_invoices(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate invoices from v4 to v6."""
    logger.info("Starting invoice migration...")

    invoices = await source.fetch("""
        SELECT
            i.uuid as id,
            i.invoice_number,
            COALESCE(i.invoice_date, i.create_date) as entity_date,
            i.due_date,
            i.status,
            i.invoice_type,
            COALESCE(i.invoice_amount, 0) as total,
            COALESCE(i.commission, 0) as commission,
            COALESCE(i.commission_rate, 0) as commission_rate,
            COALESCE(i.paid_amount, 0) as paid_amount,
            COALESCE(i.commission_paid_amount, 0) as commission_paid_amount,
            NOT COALESCE(i.draft, false) as published,
            i.creation_type,
            o.uuid as order_id,
            f.uuid as factory_id,
            c.uuid as customer_id,
            i.created_by as created_by_id,
            COALESCE(i.create_date, now()) as created_at,
            i.batch_id
        FROM public.invoices i
        LEFT JOIN public.orders o ON i.order_id = o.order_id
        LEFT JOIN public.factories f ON i.factory_id = f.factory_id
        LEFT JOIN public.customers c ON i.customer_id = c.customer_id
    """)

    if not invoices:
        logger.info("No invoices to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.invoices (
            id, invoice_number, entity_date, due_date, status, invoice_type, total,
            commission, commission_rate, paid_amount, commission_paid_amount,
            published, creation_type, order_id, factory_id, customer_id, balance_id,
            created_by_id, created_at, batch_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NULL, $17, $18, $19)
        ON CONFLICT (id) DO UPDATE SET
            invoice_number = EXCLUDED.invoice_number,
            entity_date = EXCLUDED.entity_date,
            due_date = EXCLUDED.due_date,
            status = EXCLUDED.status,
            invoice_type = EXCLUDED.invoice_type,
            total = EXCLUDED.total,
            commission = EXCLUDED.commission,
            commission_rate = EXCLUDED.commission_rate,
            paid_amount = EXCLUDED.paid_amount,
            commission_paid_amount = EXCLUDED.commission_paid_amount,
            published = EXCLUDED.published,
            creation_type = EXCLUDED.creation_type,
            order_id = EXCLUDED.order_id,
            factory_id = EXCLUDED.factory_id,
            customer_id = EXCLUDED.customer_id
        """,
        [(
            inv["id"],
            inv["invoice_number"],
            inv["entity_date"],
            inv["due_date"],
            inv["status"],
            inv["invoice_type"],
            inv["total"],
            inv["commission"],
            inv["commission_rate"],
            inv["paid_amount"],
            inv["commission_paid_amount"],
            inv["published"],
            inv["creation_type"],
            inv["order_id"],
            inv["factory_id"],
            inv["customer_id"],
            inv["created_by_id"],
            inv["created_at"],
            inv["batch_id"],
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
            id.item_number,
            COALESCE(id.quantity_shipped, 0) as quantity_shipped,
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
            id.shipped_date,
            id.status
        FROM public.invoice_details id
        JOIN public.invoices inv ON id.invoice_id = inv.invoice_id
        LEFT JOIN public.products p ON id.product_id = p.product_id
        LEFT JOIN public.customers eu ON id.end_user = eu.customer_id
    """)

    if not details:
        logger.info("No invoice details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.invoice_details (
            id, invoice_id, item_number, quantity_shipped, unit_price, subtotal, total,
            total_line_commission, commission_rate, commission, commission_discount_rate,
            commission_discount, discount_rate, discount, product_id, order_detail_id,
            end_user_id, shipped_date, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NULL, $16, $17, $18)
        """,
        [(
            d["id"],
            d["invoice_id"],
            d["item_number"],
            d["quantity_shipped"],
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
            d["shipped_date"],
            d["status"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} invoice details")
    return len(details)


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
        results["users"] = await migrate_users(source, dest)
        results["customers"] = await migrate_customers(source, dest)
        results["factories"] = await migrate_factories(source, dest)
        results["product_uoms"] = await migrate_product_uoms(source, dest)
        results["product_categories"] = await migrate_product_categories(source, dest)
        results["products"] = await migrate_products(source, dest)
        results["product_cpns"] = await migrate_product_cpns(source, dest)
        results["customer_split_rates"] = await migrate_customer_split_rates(source, dest)
        results["customer_factory_sales_reps"] = await migrate_customer_factory_sales_reps(source, dest)
        results["orders"] = await migrate_orders(source, dest)
        results["order_details"] = await migrate_order_details(source, dest)
        results["quotes"] = await migrate_quotes(source, dest)
        results["quote_details"] = await migrate_quote_details(source, dest)
        results["invoices"] = await migrate_invoices(source, dest)
        results["invoice_details"] = await migrate_invoice_details(source, dest)

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
    args = parser.parse_args()

    if not args.source_url or not args.dest_url:
        parser.error("--source-url and --dest-url are required (or set V4_DATABASE_URL and V6_DATABASE_URL)")

    _ = asyncio.run(run_migration_for_tenant(
        source_tenant=args.source_tenant,
        dest_tenant=args.dest_tenant,
        source_base_url=args.source_url,
        dest_base_url=args.dest_url,
    ))
