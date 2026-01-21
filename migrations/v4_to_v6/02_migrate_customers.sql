-- Migration: Customers from v4 (public.customers) to v6 (pycore.customers)
-- Run order: 02
-- Dependencies: 01_migrate_users.sql (requires users for created_by)

-- v4 schema: public.customers (customer_id, company_name, contact_email, contact_name, contact_number,
--            customer_type, alias, is_parent, parent_id, draft, inside_rep_id, outside_rep_id, uuid,
--            outside_rep_splits, status, territory_id, branch_id, create_date, created_by, creation_type)
-- v6 schema: pycore.customers (company_name, parent_id, published, is_parent, id, created_by_id, created_at)

-- Note: v4 uses customer_id (integer) but has uuid field. v6 uses uuid as id.
-- We'll use the uuid field from v4 as the id in v6.

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
    c.uuid,
    c.company_name,
    NULL,  -- Set parent_id to NULL initially
    COALESCE(c.status, true),  -- Map status to published
    COALESCE(c.is_parent, false),
    c.created_by,
    COALESCE(c.create_date, now())
FROM public.customers c
WHERE c.parent_id IS NULL
ON CONFLICT (id) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    published = EXCLUDED.published,
    is_parent = EXCLUDED.is_parent;

-- Then, insert child customers with their parent references
-- Note: parent_id in v4 is integer, need to map via uuid
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
    c.uuid,
    c.company_name,
    parent.uuid,  -- Map integer parent_id to parent's uuid
    COALESCE(c.status, true),
    COALESCE(c.is_parent, false),
    c.created_by,
    COALESCE(c.create_date, now())
FROM public.customers c
JOIN public.customers parent ON c.parent_id = parent.customer_id
WHERE c.parent_id IS NOT NULL
ON CONFLICT (id) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    parent_id = EXCLUDED.parent_id,
    published = EXCLUDED.published,
    is_parent = EXCLUDED.is_parent;
