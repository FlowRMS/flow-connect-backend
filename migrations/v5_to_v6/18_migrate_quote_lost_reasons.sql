-- Migration: Quote Lost Reasons from v5 (crm.quote_lost_reasons) to v6 (pycrm.quote_lost_reasons)
-- Run order: 18
-- Dependencies: 01_migrate_users.sql

-- v5 schema: crm.quote_lost_reasons (id, title, entry_date, created_by, creation_type, user_owner_ids, is_used, position)
-- v6 schema: pycrm.quote_lost_reasons (created_by_id, title, position, id, created_at)

INSERT INTO pycrm.quote_lost_reasons (
    id,
    created_by_id,
    title,
    "position",
    created_at
)
SELECT
    qlr.id,
    qlr.created_by,
    qlr.title,
    COALESCE(qlr."position", 0)::integer,
    COALESCE(qlr.entry_date, now())
FROM crm.quote_lost_reasons qlr
ON CONFLICT (id) DO UPDATE SET
    created_by_id = EXCLUDED.created_by_id,
    title = EXCLUDED.title,
    "position" = EXCLUDED."position";
