import logging

import asyncpg

logger = logging.getLogger(__name__)


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
        JOIN core.sales_rep_selections srs ON srs.id = srsr.sales_pep_selection_id
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


async def migrate_addresses(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate addresses from v5 (core.addresses) to v6 (pycore.addresses).

    v5 entity_type: 0 = customer, 1 = factory
    v6 source_type: 1 = CUSTOMER, 2 = FACTORY (IntEnum auto())
    v5 address_type: 0 = billing, 1 = shipping, etc.
    v6 address_type: 1 = BILLING, 2 = SHIPPING, 3 = MAILING, 4 = OTHER
    """
    logger.info("Starting address migration...")

    addresses = await source.fetch("""
        SELECT
            a.id,
            a.source_id,
            CASE
                WHEN a.entity_type = 0 THEN 1
                WHEN a.entity_type = 1 THEN 2
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

    await dest.executemany(
        """
        INSERT INTO pycore.addresses (
            id, source_id, source_type, address_type, country, city,
            line_1, line_2, state, zip_code, notes, is_primary,
            created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NULL, false, $11)
        ON CONFLICT (id) DO UPDATE SET
            source_id = EXCLUDED.source_id,
            source_type = EXCLUDED.source_type,
            address_type = EXCLUDED.address_type,
            country = EXCLUDED.country,
            city = EXCLUDED.city,
            line_1 = EXCLUDED.line_1,
            line_2 = EXCLUDED.line_2,
            state = EXCLUDED.state,
            zip_code = EXCLUDED.zip_code
        """,
        [(
            a["id"],
            a["source_id"],
            a["source_type"],
            a["address_type"],
            a["country"],
            a["city"],
            a["line_1"],
            a["line_2"],
            a["state"],
            a["zip_code"],
            # a["created_by_id"],
            a["created_at"],
        ) for a in addresses],
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
        [(
            c["id"],
            c["first_name"],
            c["last_name"],
            c["email"],
            c["phone"],
            c["role"],
            c["created_by_id"],
            c["created_at"],
        ) for c in contacts],
    )

    logger.info(f"Migrated {len(contacts)} contacts")
    return len(contacts)


async def migrate_contact_links(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate contact-to-customer/factory relationships via link_relations.

    v5 contacts have entity_type (0=customer, 1=factory) and source_id.
    v6 uses link_relations table with entity types:
    - 3 = CONTACT
    - 12 = CUSTOMER
    - 13 = FACTORY (assumed based on pattern)
    """
    logger.info("Starting contact link migration...")

    # Customer contacts (entity_type = 0)
    customer_links = await source.fetch("""
        SELECT
            gen_random_uuid() as id,
            c.id as contact_id,
            c.source_id as customer_id,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM core.contacts c
        WHERE c.entity_type = 0 AND c.source_id IS NOT NULL
    """)

    if customer_links:
        await dest.executemany(
            """
            INSERT INTO pycrm.link_relations (
                id, source_entity_type, source_entity_id,
                target_entity_type, target_entity_id,
                created_by_id, created_at
            ) VALUES ($1, 3, $2, 12, $3, $4, $5)
            ON CONFLICT DO NOTHING
            """,
            [(
                link["id"],
                link["contact_id"],
                link["customer_id"],
                link["created_by_id"],
                link["created_at"],
            ) for link in customer_links],
        )

    logger.info(f"Migrated {len(customer_links)} contact-customer links")
    return len(customer_links)
