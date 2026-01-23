import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_order_balances(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate order balances from v5 (commission.order_balances) to v6 (pycommission.order_balances)."""
    logger.info("Starting order balance migration...")

    # Max value for NUMERIC(18,6) is 10^12 - 1 (999999999999.999999)
    max_val = 999999999999

    # Log any records with overflow values before clamping
    overflow_records = await source.fetch(f"""
        SELECT ob.id
        FROM commission.order_balances ob
        WHERE ABS(COALESCE(ob.quantity, 0)) >= {max_val}
           OR ABS(COALESCE(ob.subtotal, 0)) >= {max_val}
           OR ABS(COALESCE(ob.total, 0)) >= {max_val}
           OR ABS(COALESCE(ob.commission, 0)) >= {max_val}
           OR ABS(COALESCE(ob.discount, 0)) >= {max_val}
           OR ABS(COALESCE(ob.commission_rate, 0)) >= {max_val}
           OR ABS(COALESCE(ob.commission_discount, 0)) >= {max_val}
           OR ABS(COALESCE(ob.shipping_balance, 0)) >= {max_val}
           OR ABS(COALESCE(ob.freight_charge, 0)) >= {max_val}
    """)
    if overflow_records:
        overflow_ids = [str(r["id"]) for r in overflow_records]
        logger.warning(
            f"Found {len(overflow_records)} order_balances with overflow values "
            f"(will be clamped to {max_val}): {overflow_ids}"
        )

    balances = await source.fetch(f"""
        SELECT
            ob.id,
            LEAST(GREATEST(COALESCE(ob.quantity, 0), -{max_val}), {max_val}) as quantity,
            LEAST(GREATEST(COALESCE(ob.subtotal, 0), -{max_val}), {max_val}) as subtotal,
            LEAST(GREATEST(COALESCE(ob.total, 0), -{max_val}), {max_val}) as total,
            LEAST(GREATEST(COALESCE(ob.commission, 0), -{max_val}), {max_val}) as commission,
            LEAST(GREATEST(COALESCE(ob.discount, 0), -{max_val}), {max_val}) as discount,
            LEAST(GREATEST(COALESCE(ob.discount_rate, 0), -{max_val}), {max_val}) as discount_rate,
            LEAST(GREATEST(COALESCE(ob.commission_rate, 0), -{max_val}), {max_val}) as commission_rate,
            LEAST(GREATEST(COALESCE(ob.commission_discount, 0), -{max_val}), {max_val}) as commission_discount,
            LEAST(GREATEST(COALESCE(ob.commission_discount_rate, 0), -{max_val}), {max_val}) as commission_discount_rate,
            LEAST(GREATEST(COALESCE(ob.shipping_balance, 0), -{max_val}), {max_val}) as shipping_balance,
            LEAST(GREATEST(COALESCE(ob.freight_charge, 0), -{max_val}), {max_val}) as freight_charge_balance
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
            o.status + 1 AS status,
            o.order_type + 1 AS order_type,
            o.header_status + 1 AS header_status,
            o.factory_id,
            o.shipping_terms,
            o.freight_terms,
            o.mark_number,
            o.ship_date,
            o.fact_so_number,
            o.quote_id,
            o.balance_id,
            o.job_id,
            COALESCE(
                u.id,
                (SELECT id FROM "user".users WHERE username = 'support@flowrms.com' LIMIT 1)
            ) as created_by_id,
            COALESCE(o.entry_date, now()) as created_at
        FROM commission.orders o
        LEFT JOIN "user".users u ON u.id = o.created_by
        LEFT JOIN crm.quotes q ON q.id = o.quote_id
        WHERE
            o.sold_to_customer_id IS NOT NULL
            AND o.factory_id IS NOT NULL
            AND (o.quote_id IS NULL OR q.sold_to_customer_id IS NOT NULL)
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
        JOIN "user".users u ON u.id = oir.user_id
        LEFT JOIN core.products p ON p.id = od.product_id
        LEFT JOIN crm.quotes q ON q.id = o.quote_id
        WHERE
            o.sold_to_customer_id IS NOT NULL
            AND o.factory_id IS NOT NULL
            AND (o.quote_id IS NULL OR q.sold_to_customer_id IS NOT NULL)
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
            CASE WHEN end_user.id IS NOT NULL THEN od.end_user_id ELSE o.sold_to_customer_id END as end_user_id,
            od.lead_time,
            od.status + 1 AS status,
            COALESCE(od.freight_charge, 0) as freight_charge,
            COALESCE(od.shipping_balance, 0) as shipping_balance,
            CASE
                WHEN od.uom_multiply AND od.uom_multiply_by > 0 THEN od.uom_multiply_by
                ELSE NULL
            END AS division_factor
        FROM commission.order_details od
        LEFT JOIN core.products p ON p.id = od.product_id
        JOIN commission.orders o ON o.id = od.order_id
        LEFT JOIN "user".users u ON u.id = o.created_by
        LEFT JOIN crm.quotes q ON q.id = o.quote_id
        LEFT JOIN core.customers end_user ON end_user.id = od.end_user_id
        WHERE
            o.sold_to_customer_id IS NOT NULL
            AND o.factory_id IS NOT NULL
            AND (o.quote_id IS NULL OR q.sold_to_customer_id IS NOT NULL)
    """)

    if not details:
        logger.info("No order details to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycommission.order_details (
            id, 
            order_id, 
            item_number, 
            quantity, 
            unit_price, 
            subtotal, 
            total,
            total_line_commission, 
            commission_rate, 
            commission, 
            commission_discount_rate,
            commission_discount, 
            discount_rate, 
            discount, 
            division_factor, 
            product_id,
            product_name_adhoc, 
            product_description_adhoc, 
            end_user_id,
            uom_id, 
            lead_time, 
            note, 
            status, 
            freight_charge, 
            shipping_balance, 
            cancelled_balance
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, NULL, NULL, $17, NULL, $18, NULL, $19, $20, $21, 0)
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
            d["id"], # 1
            d["order_id"], # 2
            d["item_number"], # 3
            d["quantity"], # 4
            d["unit_price"], # 5
            d["subtotal"], # 6
            d["total"], # 7
            d["total_line_commission"], # 8
            d["commission_rate"], # 9
            d["commission"], # 10
            d["commission_discount_rate"], # 11
            d["commission_discount"], # 12
            d["discount_rate"], # 13
            d["discount"], # 14
            d["division_factor"], # 15
            d["product_id"], # 16
            d["end_user_id"], # 17
            d["lead_time"], # 18
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
            COALESCE(split_user.id, (SELECT id FROM "user".users WHERE username = 'support@flowrms.com' LIMIT 1)) as user_id,
            COALESCE(osr.split_rate, 0) as split_rate,
            COALESCE(osr."position", 0) as position,
            COALESCE(osr.entry_date, now()) as created_at
        FROM commission.order_split_rates osr
        JOIN commission.order_details od ON od.id = osr.order_detail_id
        JOIN commission.orders o ON o.id = od.order_id
        LEFT JOIN "user".users u ON u.id = o.created_by
        LEFT JOIN core.products p ON p.id = od.product_id
        LEFT JOIN crm.quotes q ON q.id = o.quote_id
        LEFT JOIN "user".users split_user ON split_user.id = osr.user_id
        WHERE
            o.sold_to_customer_id IS NOT NULL
            AND o.factory_id IS NOT NULL
            AND (o.quote_id IS NULL OR q.sold_to_customer_id IS NOT NULL)
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


async def migrate_order_acknowledgements(
    source: asyncpg.Connection, dest: asyncpg.Connection
) -> int:
    """Migrate order acknowledgements from v5 to v6.

    Schema changed to many-to-many: order_detail_id moved to junction table
    order_acknowledgement_details.
    """
    logger.info("Starting order acknowledgement migration...")

    acknowledgements = await source.fetch("""
        SELECT
            oa.id,
            od.order_id,
            oa.order_detail_id,
            oa.order_acknowledgement_number,
            oa.entity_date,
            COALESCE(od.quantity, 0) as quantity,
            oa.creation_type,
            COALESCE(
                u.id,
                (SELECT id FROM "user".users WHERE username = 'support@flowrms.com' LIMIT 1)
            ) as created_by_id,
            COALESCE(oa.entry_date, now()) as created_at
        FROM commission.order_acknowledgements oa
        JOIN commission.order_details od ON od.id = oa.order_detail_id
        JOIN commission.orders o ON o.id = od.order_id
        LEFT JOIN "user".users u ON u.id = oa.created_by
        LEFT JOIN crm.quotes q ON q.id = o.quote_id
        WHERE
            o.sold_to_customer_id IS NOT NULL
            AND o.factory_id IS NOT NULL
            AND (o.quote_id IS NULL OR q.sold_to_customer_id IS NOT NULL)
            AND o.entry_date < now() - INTERVAL '2 days'
    """)

    if not acknowledgements:
        logger.info("No order acknowledgements to migrate")
        return 0

    # Insert into order_acknowledgements (without order_detail_id)
    await dest.executemany(
        """
        INSERT INTO pycommission.order_acknowledgements (
            id, order_id, order_acknowledgement_number,
            entity_date, quantity, creation_type, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (id) DO UPDATE SET
            order_id = EXCLUDED.order_id,
            order_acknowledgement_number = EXCLUDED.order_acknowledgement_number,
            entity_date = EXCLUDED.entity_date,
            quantity = EXCLUDED.quantity,
            creation_type = EXCLUDED.creation_type
        """,
        [(
            a["id"],
            a["order_id"],
            a["order_acknowledgement_number"],
            a["entity_date"],
            a["quantity"],
            a["creation_type"],
            a["created_by_id"],
            a["created_at"],
        ) for a in acknowledgements],
    )

    # Insert into junction table order_acknowledgement_details
    await dest.executemany(
        """
        INSERT INTO pycommission.order_acknowledgement_details (
            id, order_acknowledgement_id, order_detail_id, created_at
        ) VALUES (gen_random_uuid(), $1, $2, $3)
        ON CONFLICT (order_acknowledgement_id, order_detail_id) DO NOTHING
        """,
        [(
            a["id"],
            a["order_detail_id"],
            a["created_at"],
        ) for a in acknowledgements],
    )

    logger.info(f"Migrated {len(acknowledgements)} order acknowledgements")
    return len(acknowledgements)
