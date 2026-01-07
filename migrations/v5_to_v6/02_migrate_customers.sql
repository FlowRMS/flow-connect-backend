-- Migration: Customers from v5 (core.customers) to v6 (pycore.customers)
-- Run order: 02
-- Dependencies: 01_migrate_users.sql (requires users for created_by_id)

-- Insert customers from v5 to v6
-- v5 schema: core.customers (id, entry_date, created_by, creation_type, company_name, is_parent, parent_id,
--            contact_email, contact_number, published, customer_branch_id, customer_territory_id,
--            logo_url, inside_rep_id, user_owner_ids, is_used, type)
-- v6 schema: pycore.customers (company_name, parent_id, published, is_parent, id, created_by_id, created_at)

-- First, insert customers without parent_id to avoid FK issues
INSERT INTO pycore.customers (
    id,
    company_name,
    parent_id,
    published,
    is_parent,
    created_by_id,
    created_at
)
SELECT
    c.id,
    c.company_name,
    NULL,  -- Set parent_id to NULL initially
    c.published,
    c.is_parent,
    c.created_by,
    COALESCE(c.entry_date, now())
FROM core.customers c
WHERE c.parent_id IS NULL
ON CONFLICT (id) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    published = EXCLUDED.published,
    is_parent = EXCLUDED.is_parent;

-- Then, insert child customers
INSERT INTO pycore.customers (
    id,
    company_name,
    parent_id,
    published,
    is_parent,
    created_by_id,
    created_at
)
SELECT
    c.id,
    c.company_name,
    c.parent_id,
    c.published,
    c.is_parent,
    c.created_by,
    COALESCE(c.entry_date, now())
FROM core.customers c
WHERE c.parent_id IS NOT NULL
ON CONFLICT (id) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    parent_id = EXCLUDED.parent_id,
    published = EXCLUDED.published,
    is_parent = EXCLUDED.is_parent;
