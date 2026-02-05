import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_customer_split_rates(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate customer split rates from v5 to v6.

    v5: core.customer_split_rates (id, user_id, customer_id, split_rate, position)
    v6: pycore.customer_split_rates adds rep_type field (1=OUTSIDE, 2=INSIDE)

    All entries from customer_split_rates are OUTSIDE reps (rep_type = 1).
    INSIDE reps come from customers.inside_rep_id in migrate_inside_customer_split_rates.
    """
    logger.info("Starting customer split rate migration...")

    split_rates = await source.fetch("""
        SELECT
            csr.id,
            csr.user_id,
            csr.customer_id,
            COALESCE(csr.split_rate, 0) as split_rate,
            COALESCE(csr."position", 0)::integer as position,
            COALESCE(csr.entry_date, now()) as created_at,
            1 as rep_type  -- Always OUTSIDE
        FROM core.customer_split_rates csr
        JOIN "user".users u ON u.id = csr.user_id
        JOIN core.customers c ON c.id = csr.customer_id
        JOIN "user".users cu ON cu.id = c.created_by
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
        [
            (
                sr["id"],
                sr["user_id"],
                sr["customer_id"],
                sr["split_rate"],
                sr["rep_type"],
                sr["position"],
                sr["created_at"],
            )
            for sr in split_rates
        ],
    )

    logger.info(f"Migrated {len(split_rates)} customer split rates")
    return len(split_rates)


async def migrate_inside_customer_split_rates(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate inside reps from customers.inside_rep_id to v6.

    v6: pycore.customer_split_rates with rep_type field (1=OUTSIDE, 2=INSIDE)

    Creates INSIDE rep entries from customers.inside_rep_id.
    Split rate is calculated as 100% divided by number of inside reps per customer.
    """
    logger.info("Starting inside customer split rate migration...")

    split_rates = await source.fetch("""
        WITH inside_reps AS (
            SELECT
                c.inside_rep_id as user_id,
                c.id as customer_id,
                COALESCE(c.entry_date, now()) as created_at
            FROM core.customers c
            JOIN "user".users u ON u.id = c.inside_rep_id
            JOIN "user".users cu ON cu.id = c.created_by
            WHERE c.inside_rep_id IS NOT NULL
        ),
        rep_counts AS (
            SELECT customer_id, COUNT(*) as cnt
            FROM inside_reps
            GROUP BY customer_id
        )
        SELECT
            gen_random_uuid() as id,
            ir.user_id,
            ir.customer_id,
            ROUND(100.0 / rc.cnt, 2) as split_rate,
            0 as position,
            ir.created_at,
            2 as rep_type  -- INSIDE
        FROM inside_reps ir
        JOIN rep_counts rc ON rc.customer_id = ir.customer_id
    """)

    if not split_rates:
        logger.info("No inside customer split rates to migrate")
        return 0

    # Filter out records that already exist (same user_id, customer_id, rep_type)
    existing = await dest.fetch("""
        SELECT user_id, customer_id, rep_type
        FROM pycore.customer_split_rates
        WHERE rep_type = 2
    """)
    existing_keys = {(r["user_id"], r["customer_id"], r["rep_type"]) for r in existing}

    new_split_rates = [
        sr
        for sr in split_rates
        if (sr["user_id"], sr["customer_id"], sr["rep_type"]) not in existing_keys
    ]

    if not new_split_rates:
        logger.info("No new inside customer split rates to migrate (all exist)")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.customer_split_rates (
            id, user_id, customer_id, split_rate, rep_type, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            split_rate = EXCLUDED.split_rate,
            "position" = EXCLUDED."position"
        """,
        [
            (
                sr["id"],
                sr["user_id"],
                sr["customer_id"],
                sr["split_rate"],
                sr["rep_type"],
                sr["position"],
                sr["created_at"],
            )
            for sr in new_split_rates
        ],
    )

    logger.info(f"Migrated {len(new_split_rates)} inside customer split rates")
    return len(new_split_rates)


async def migrate_factory_split_rates(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate factory split rates from v5 sales_rep_selection_split_rates to v6.

    v5 uses sales_rep_selections + sales_rep_selection_split_rates for factory assignments.
    v6 has pycore.factory_split_rates (id, user_id, factory_id, split_rate, position).

    This extracts unique factory-user assignments from sales_rep_selection_split_rates.
    """
    logger.info("Starting factory split rate migration...")

    split_rates = await source.fetch("""
        SELECT
            gen_random_uuid() as id,
            f.inside_rep_id as user_id,
            f.id as factory_id,
            100 as split_rate,
            0 as position,
            COALESCE(f.entry_date, now()) as created_at
        FROM core.factories f
        JOIN "user".users u ON u.id = f.inside_rep_id
        WHERE f.inside_rep_id IS NOT NULL
    """)
    if not split_rates:
        logger.info("No factory split rates to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.factory_split_rates (
            id, user_id, factory_id, split_rate, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            user_id = EXCLUDED.user_id,
            factory_id = EXCLUDED.factory_id,
            split_rate = EXCLUDED.split_rate,
            "position" = EXCLUDED."position"
        """,
        [
            (
                sr["id"],
                sr["user_id"],
                sr["factory_id"],
                sr["split_rate"],
                sr["position"],
                sr["created_at"],
            )
            for sr in split_rates
        ],
    )

    logger.info(f"Migrated {len(split_rates)} factory split rates")
    return len(split_rates)


async def migrate_customer_factory_sales_reps(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate sales rep selections from v5 to v6 customer_factory_sales_reps.

    v5 has sales_rep_selections (customer_id, factory_id) with separate
    sales_rep_selection_split_rates (user_id, split_rate, position).
    v6 denormalizes this into customer_factory_sales_reps with one row per user.
    """
    logger.info("Starting customer factory sales rep migration...")

    sales_reps = await source.fetch("""
        SELECT
            srsr.id,
            srs.customer_id,
            srs.factory_id,
            srsr.user_id,
            COALESCE(srsr.split_rate, 0) as rate,
            COALESCE(srsr."position", 0) as position,
            COALESCE(srsr.entry_date, now()) as created_at
        FROM core.sales_rep_selection_split_rates srsr
        JOIN "user".users u ON u.id = srsr.user_id
        JOIN core.sales_rep_selections srs ON srs.id = srsr.sales_pep_selection_id
        JOIN core.customers c ON c.id = srs.customer_id
        JOIN "user".users cu ON cu.id = c.created_by
    """)

    if not sales_reps:
        logger.info("No customer factory sales reps to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.customer_factory_sales_reps (
            id, customer_id, factory_id, user_id, rate, "position", created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (customer_id, factory_id, user_id) DO UPDATE SET
            rate = EXCLUDED.rate,
            "position" = EXCLUDED."position"
        """,
        [
            (
                sr["id"],
                sr["customer_id"],
                sr["factory_id"],
                sr["user_id"],
                sr["rate"],
                sr["position"],
                sr["created_at"],
            )
            for sr in sales_reps
        ],
    )

    logger.info(f"Migrated {len(sales_reps)} customer factory sales reps")
    return len(sales_reps)


async def migrate_addresses(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate addresses from v5 (core.addresses) to v6 (pycore.addresses).

    v5 entity_type: 0 = factory, 1 = customer
    v6 source_type: 1 = CUSTOMER, 2 = FACTORY (IntEnum auto())
    v5 address_type: 0 = billing, 1 = shipping, etc.
    v6 address_types table: type = 1 = BILLING, 2 = SHIPPING, 3 = MAILING, 4 = OTHER
    """
    logger.info("Starting address migration...")

    addresses = await source.fetch("""
        SELECT
            a.id,
            a.source_id,
            CASE
                WHEN a.entity_type = 0 THEN 2
                WHEN a.entity_type = 1 THEN 1
                ELSE 1
            END AS source_type,
            CASE
                WHEN a.address_type = 0 THEN 1
                WHEN a.address_type = 1 THEN 2
                WHEN a.address_type = 2 THEN 3
                ELSE 4
            END AS address_type,
            COALESCE(a.country_code, 'US') as country,
            a.locality as city,
            a.address_line_one as line_1,
            a.address_line_two as line_2,
            a.administrative_area as state,
            a.postal_code as zip_code,
            a.created_by as created_by_id,
            COALESCE(a.entry_date, now()) as created_at
        FROM core.addresses a
    """)

    if not addresses:
        logger.info("No addresses to migrate")
        return 0

    # Insert addresses without address_type column (now in separate table)
    await dest.executemany(
        """
        INSERT INTO pycore.addresses (
            id, source_id, source_type, country, city,
            line_1, line_2, state, zip_code, notes, is_primary,
            created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NULL, false, $10)
        ON CONFLICT (id) DO UPDATE SET
            source_id = EXCLUDED.source_id,
            source_type = EXCLUDED.source_type,
            country = EXCLUDED.country,
            city = EXCLUDED.city,
            line_1 = EXCLUDED.line_1,
            line_2 = EXCLUDED.line_2,
            state = EXCLUDED.state,
            zip_code = EXCLUDED.zip_code
        """,
        [
            (
                a["id"],
                a["source_id"],
                a["source_type"],
                a["country"],
                a["city"],
                a["line_1"],
                a["line_2"],
                a["state"],
                a["zip_code"],
                a["created_at"],
            )
            for a in addresses
        ],
    )

    # Insert address types into the junction table
    await dest.executemany(
        """
        INSERT INTO pycore.address_types (id, address_id, type)
        VALUES (gen_random_uuid(), $1, $2)
        ON CONFLICT DO NOTHING
        """,
        [(a["id"], a["address_type"]) for a in addresses],
    )

    logger.info(f"Migrated {len(addresses)} addresses")
    return len(addresses)


async def migrate_contacts(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate contacts from v5 (core.contacts) to v6 (pycrm.contacts).

    Note: v6 contacts use a link system for customer/factory associations.
    This migration only creates the contact records. Link relations need
    to be created separately based on the source_id and entity_type.
    """
    logger.info("Starting contact migration...")

    contacts = await source.fetch("""
        SELECT
            c.id,
            c.firstname as first_name,
            c.lastname as last_name,
            c.email,
            c.phone,
            c.title as role,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM core.contacts c
    """)

    if not contacts:
        logger.info("No contacts to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.contacts (
            id, first_name, last_name, email, phone, role,
            territory, tags, notes, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, NULL, NULL, NULL, $7, $8)
        ON CONFLICT (id) DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone,
            role = EXCLUDED.role
        """,
        [
            (
                c["id"],
                c["first_name"],
                c["last_name"],
                c["email"],
                c["phone"],
                c["role"],
                c["created_by_id"],
                c["created_at"],
            )
            for c in contacts
        ],
    )

    logger.info(f"Migrated {len(contacts)} contacts")
    return len(contacts)


async def migrate_contact_links(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate contact-to-customer/factory relationships via link_relations.

    Uses source_id from contacts and left joins to factories/customers tables
    to determine the target entity type.

    v6 EntityType values:
    - 3 = CONTACT
    - 11 = FACTORY
    - 12 = CUSTOMER
    """
    logger.info("Starting contact link migration...")

    # Get contacts with source_id and determine if linked to factory or customer
    contact_links = await source.fetch("""
        SELECT
            gen_random_uuid() as id,
            c.id as contact_id,
            c.source_id,
            CASE
                WHEN f.id IS NOT NULL THEN 11  -- FACTORY
                WHEN cust.id IS NOT NULL THEN 12  -- CUSTOMER
                ELSE NULL
            END AS target_entity_type,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM core.contacts c
        LEFT JOIN core.factories f ON f.id = c.source_id
        LEFT JOIN core.customers cust ON cust.id = c.source_id
        WHERE c.source_id IS NOT NULL
          AND (f.id IS NOT NULL OR cust.id IS NOT NULL)
    """)

    if not contact_links:
        logger.info("No contact links to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.link_relations (
            id, source_entity_type, source_entity_id,
            target_entity_type, target_entity_id,
            created_by_id, created_at
        ) VALUES ($1, 3, $2, $3, $4, $5, $6)
        ON CONFLICT DO NOTHING
        """,
        [
            (
                link["id"],
                link["contact_id"],
                link["target_entity_type"],
                link["source_id"],
                link["created_by_id"],
                link["created_at"],
            )
            for link in contact_links
        ],
    )

    # Log breakdown by type
    factory_count = sum(1 for link in contact_links if link["target_entity_type"] == 11)
    customer_count = sum(
        1 for link in contact_links if link["target_entity_type"] == 12
    )
    logger.info(
        f"Migrated {len(contact_links)} contact links "
        f"({factory_count} factory, {customer_count} customer)"
    )
    return len(contact_links)
