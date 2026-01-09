-- Migration: Addresses from v4 (public.addresses) to v6 (pycore.addresses)
-- Run order: 08
-- Dependencies: 02_migrate_customers.sql, 03_migrate_factories.sql

-- v4 schema: public.addresses (uuid, source_id, address_type, address_line_one, address_line_two,
--            city, state, zip, create_date, created_by, creation_type)
-- v6 schema: pycore.addresses (id, source_id, source_type, address_type, line_1, line_2, city, state, zip_code,
--            country, notes, is_primary, created_at)

-- Note: v4 source_id is integer that can reference either customer_id or factory_id
-- The address_type field typically indicates whether it's a customer or factory address
-- We need to map integer source_id to uuid

-- First, migrate customer addresses (address_type contains 'customer' or similar pattern)
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
    a.uuid,
    c.uuid,  -- Map integer source_id to customer's uuid
    'customer' AS source_type,
    a.address_type,
    COALESCE(a.address_line_one, 'Unknown'),
    a.address_line_two,
    COALESCE(a.city, 'Unknown'),
    a.state,
    COALESCE(a.zip, 'Unknown'),
    'US',  -- Default country
    NULL,  -- No notes in v4
    false,  -- Default is_primary to false
    COALESCE(a.create_date, now())
FROM public.addresses a
JOIN public.customers c ON a.source_id = c.customer_id
WHERE lower(a.address_type) LIKE '%customer%'
   OR lower(a.address_type) IN ('billing', 'shipping', 'bill_to', 'ship_to', 'bill-to', 'ship-to')
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

-- Then, migrate factory addresses
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
    a.uuid,
    f.uuid,  -- Map integer source_id to factory's uuid
    'factory' AS source_type,
    a.address_type,
    COALESCE(a.address_line_one, 'Unknown'),
    a.address_line_two,
    COALESCE(a.city, 'Unknown'),
    a.state,
    COALESCE(a.zip, 'Unknown'),
    'US',  -- Default country
    NULL,  -- No notes in v4
    false,  -- Default is_primary to false
    COALESCE(a.create_date, now())
FROM public.addresses a
JOIN public.factories f ON a.source_id = f.factory_id
WHERE lower(a.address_type) LIKE '%factory%'
   OR lower(a.address_type) LIKE '%vendor%'
   OR lower(a.address_type) LIKE '%supplier%'
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
