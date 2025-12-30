-- Migration: Addresses from v5 (core.addresses) to v6 (pycore.addresses)
-- Run order: 10
-- Dependencies: 02_migrate_customers.sql, 04_migrate_factories.sql (addresses link to customers/factories via source_id)

-- v5 schema: core.addresses (id, entry_date, created_by, creation_type, entity_type, source_id, address_type,
--            address_line_one, address_line_two, locality, administrative_area, postal_code,
--            country_code, subdivision_code, ...)
-- v6 schema: pycore.addresses (id, source_id, source_type, address_type, line_1, line_2, city, state, zip_code,
--            country, notes, is_primary, created_at)

INSERT INTO pycore.addresses (
    id,
    source_id,
    source_type,
    address_type,
    line_1,
    line_2,
    city,
    state,
    zip_code,
    country,
    notes,
    is_primary,
    created_at
)
SELECT
    a.id,
    a.source_id,
    a.entity_type AS source_type,  -- Map entity_type to source_type
    a.address_type,
    COALESCE(a.address_line_one, 'Unknown'),
    a.address_line_two,
    COALESCE(a.locality, 'Unknown'),  -- Map locality to city
    a.administrative_area,  -- Map administrative_area to state
    COALESCE(a.postal_code, 'Unknown'),  -- Map postal_code to zip_code
    COALESCE(a.country_code, 'US'),  -- Map country_code to country
    NULL,  -- No notes in v5
    false,  -- Default is_primary to false
    COALESCE(a.entry_date, now())
FROM core.addresses a
ON CONFLICT (id) DO UPDATE SET
    source_id = EXCLUDED.source_id,
    source_type = EXCLUDED.source_type,
    address_type = EXCLUDED.address_type,
    line_1 = EXCLUDED.line_1,
    line_2 = EXCLUDED.line_2,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    zip_code = EXCLUDED.zip_code,
    country = EXCLUDED.country;
