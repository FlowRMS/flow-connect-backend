import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_order_balances(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate order balances from v5 (commission.order_balances) to v6 (pycommission.order_balances)."""
    logger.info("Starting order balance migration...")

    balances = await source.fetch("""
        SELECT
            ob.id,
            COALESCE(ob.quantity, 0) as quantity,
            COALESCE(ob.subtotal, 0) as subtotal,
            COALESCE(ob.total, 0) as total,
            COALESCE(ob.commission, 0) as commission,
            COALESCE(ob.discount, 0) as discount,
            COALESCE(ob.discount_rate, 0) as discount_rate,
            COALESCE(ob.commission_rate, 0) as commission_rate,
            COALESCE(ob.commission_discount, 0) as commission_discount,
            COALESCE(ob.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(ob.shipping_balance, 0) as shipping_balance,
            COALESCE(ob.freight_charge, 0) as freight_charge_balance
        FROM commission.order_balances ob
    """)

    if not balances:
        logger.info("No order balances to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.order_balances (
            id, quantity, subtotal, total, commission, discount,
            discount_rate, commission_rate, commission_discount,
            commission_discount_rate, shipping_balance, cancelled_balance,
            freight_charge_balance
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 0, $12)
        ON CONFLICT (id) DO UPDATE SET
            quantity = EXCLUDED.quantity,
            subtotal = EXCLUDED.subtotal,
            total = EXCLUDED.total,
            commission = EXCLUDED.commission,
            discount = EXCLUDED.discount,
            discount_rate = EXCLUDED.discount_rate,
            commission_rate = EXCLUDED.commission_rate,
            commission_discount = EXCLUDED.commission_discount,
            commission_discount_rate = EXCLUDED.commission_discount_rate,
            shipping_balance = EXCLUDED.shipping_balance,
            freight_charge_balance = EXCLUDED.freight_charge_balance
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
            b["shipping_balance"],
            b["freight_charge_balance"],
        ) for b in balances],
    )

    logger.info(f"Migrated {len(balances)} order balances")
    return len(balances)


async def migrate_orders(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate orders from v5 (commission.orders) to v6 (pycommission.orders)."""
    logger.info("Starting order migration...")

    orders = await source.fetch("""
        SELECT
            o.id,
            o.order_number,
            o.entity_date,
            o.due_date,
            o.sold_to_customer_id,
            o.bill_to_customer_id,
            o.published,
            o.creation_type,
            o.status,
            o.order_type,
            o.header_status,
            o.factory_id,
            o.shipping_terms,
            o.freight_terms,
            o.mark_number,
            o.ship_date,
            o.fact_so_number,
            o.quote_id,
            o.balance_id,
            o.job_id,
            o.created_by as created_by_id,
            COALESCE(o.entry_date, now()) as created_at
        FROM commission.orders o
        JOIN "user".users u ON u.id = o.created_by
        WHERE o.sold_to_customer_id IS NOT NULL AND o.balance_id <> 'c2623ea8-9750-407b-864d-b4b2276e1a67'::uuid
    """)

    if not orders:
        logger.info("No orders to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.orders (
            id, order_number, entity_date, due_date, sold_to_customer_id,
            bill_to_customer_id, published, creation_type, status, order_type,
            header_status, factory_id, shipping_terms, freight_terms, mark_number,
            ship_date, projected_ship_date, fact_so_number, quote_id, balance_id,
            job_id, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NULL, $17, $18, $19, $20, $21, $22)
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
            quote_id = EXCLUDED.quote_id,
            job_id = EXCLUDED.job_id
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
            o["quote_id"],
            o["balance_id"],
            o["job_id"],
            o["created_by_id"],
            o["created_at"],
        ) for o in orders],
    )

    logger.info(f"Migrated {len(orders)} orders")
    return len(orders)


async def migrate_order_inside_reps(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate order inside reps from v5 (commission.order_inside_reps) to v6 (pycommission.order_inside_reps)."""
    logger.info("Starting order inside rep migration...")

    inside_reps = await source.fetch("""
        SELECT
            oir.id,
            od.id as order_detail_id,
            oir.user_id,
            COALESCE(oir.entry_date, now()) as created_at
        FROM commission.order_inside_reps oir
        JOIN commission.orders o ON o.id = oir.order_id
        JOIN commission.order_details od ON od.order_id = o.id
        JOIN "user".users u ON u.id = o.created_by
        JOIN core.products p ON p.id = od.product_id
        WHERE 
        o.sold_to_customer_id IS NOT NULL 
        AND
        o.balance_id <> 'c2623ea8-9750-407b-864d-b4b2276e1a67'::uuid
        AND
        o.entry_date < now() - INTERVAL '4 day' 
        AND 
        p.entry_date < now() - INTERVAL '4 day'
    """)

    if not inside_reps:
        logger.info("No order inside reps to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.order_inside_reps (
            id, order_detail_id, user_id, split_rate, position, created_at
        ) VALUES ($1, $2, $3, 100, 0, $4)
        ON CONFLICT (id) DO UPDATE SET
            order_detail_id = EXCLUDED.order_detail_id,
            user_id = EXCLUDED.user_id
        """,
        [(
            ir["id"],
            ir["order_detail_id"],
            ir["user_id"],
            ir["created_at"],
        ) for ir in inside_reps],
    )

    logger.info(f"Migrated {len(inside_reps)} order inside reps")
    return len(inside_reps)


async def migrate_order_details(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate order details from v5 (commission.order_details) to v6 (pycommission.order_details)."""
    logger.info("Starting order detail migration...")

    details = await source.fetch("""
        SELECT
            od.id,
            od.order_id,
            od.item_number,
            COALESCE(od.quantity, 0) as quantity,
            COALESCE(od.unit_price, 0) as unit_price,
            COALESCE(od.subtotal, 0) as subtotal,
            COALESCE(od.total, 0) as total,
            COALESCE(od.commission, 0) as total_line_commission,
            COALESCE(od.commission_rate, 0) as commission_rate,
            COALESCE(od.commission, 0) as commission,
            COALESCE(od.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(od.commission_discount, 0) as commission_discount,
            COALESCE(od.discount_rate, 0) as discount_rate,
            COALESCE(od.discount, 0) as discount,
            od.product_id,
            od.end_user_id,
            od.lead_time,
            od.status,
            COALESCE(od.freight_charge, 0) as freight_charge,
            COALESCE(od.shipping_balance, 0) as shipping_balance,
            CASE
                WHEN od.uom_multiply AND od.uom_multiply_by > 0 THEN od.uom_multiply_by
                ELSE NULL
            END AS division_factor
        FROM commission.order_details od
        JOIN core.products p ON p.id = od.product_id
        JOIN commission.orders o ON o.id = od.order_id
        JOIN "user".users u ON u.id = o.created_by
        WHERE 
        o.sold_to_customer_id IS NOT NULL 
        AND
        o.entry_date < now() - INTERVAL '2 day' 
        AND 
        p.entry_date < now() - INTERVAL '2 day'
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
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NULL, NULL, NULL, $17, NULL, $18, NULL, $19, $20, $21, 0)
        ON CONFLICT (id) DO UPDATE SET
            order_id = EXCLUDED.order_id,
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
            division_factor = EXCLUDED.division_factor,
            product_id = EXCLUDED.product_id,
            end_user_id = EXCLUDED.end_user_id,
            lead_time = EXCLUDED.lead_time,
            status = EXCLUDED.status,
            freight_charge = EXCLUDED.freight_charge,
            shipping_balance = EXCLUDED.shipping_balance
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
            d["division_factor"],
            d["product_id"],
            d["end_user_id"],
            d["lead_time"],
            d["status"],
            d["freight_charge"],
            d["shipping_balance"],
        ) for d in details],
    )

    logger.info(f"Migrated {len(details)} order details")
    return len(details)


async def migrate_order_split_rates(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate order split rates from v5 (commission.order_split_rates) to v6 (pycommission.order_split_rates)."""
    logger.info("Starting order split rate migration...")

    split_rates = await source.fetch("""
        SELECT
            osr.id,
            osr.order_detail_id,
            osr.user_id,
            COALESCE(osr.split_rate, 0) as split_rate,
            COALESCE(osr."position", 0) as position,
            COALESCE(osr.entry_date, now()) as created_at
        FROM commission.order_split_rates osr
        JOIN commission.order_details od ON od.id = osr.order_detail_id
        JOIN commission.orders o ON o.id = od.order_id
        JOIN "user".users u ON u.id = o.created_by
        JOIN core.products p ON p.id = od.product_id
        WHERE 
        o.sold_to_customer_id IS NOT NULL 
        AND
        o.balance_id <> 'c2623ea8-9750-407b-864d-b4b2276e1a67'::uuid
        AND
        o.entry_date < now() - INTERVAL '4 day' 
        AND 
        p.entry_date < now() - INTERVAL '4 day'
    """)

    if not split_rates:
        logger.info("No order split rates to migrate")
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
        [(
            sr["id"],
            sr["order_detail_id"],
            sr["user_id"],
            sr["split_rate"],
            sr["position"],
            sr["created_at"],
        ) for sr in split_rates],
    )

    logger.info(f"Migrated {len(split_rates)} order split rates")
    return len(split_rates)
