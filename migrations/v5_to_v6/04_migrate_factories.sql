-- Migration: Factories from v5 (core.factories) to v6 (pycore.factories)
-- Run order: 04
-- Dependencies: 01_migrate_users.sql, 03_migrate_files.sql (for logo_id)

-- v5 schema: core.factories (id, entry_date, created_by, creation_type, title, account_number, email, phone,
--            external_terms, additional_information, published, freight_terms, freight_discount_type,
--            lead_time, payment_terms, commission_rate, commission_discount_rate, overall_discount_rate,
--            logo_url, inside_rep_id, user_owner_ids, ...)
-- v6 schema: pycore.factories (title, account_number, email, phone, logo_id, lead_time, payment_terms,
--            base_commission_rate, commission_discount_rate, overall_discount_rate, additional_information,
--            freight_terms, external_payment_terms, published, freight_discount_type, creation_type, id,
--            created_by_id, created_at)

INSERT INTO pycore.factories (
    id,
    title,
    account_number,
    email,
    phone,
    logo_id,
    lead_time,
    payment_terms,
    base_commission_rate,
    commission_discount_rate,
    overall_discount_rate,
    additional_information,
    freight_terms,
    external_payment_terms,
    published,
    freight_discount_type,
    creation_type,
    created_by_id,
    created_at
)
SELECT
    f.id,
    f.title,
    f.account_number,
    f.email,
    f.phone,
    NULL,  -- logo_id needs to be mapped from logo_url if needed
    CASE
        WHEN f.lead_time ~ '^\d+$' THEN f.lead_time::integer
        ELSE NULL
    END AS lead_time,  -- Convert varchar to integer if numeric
    CASE
        WHEN f.payment_terms ~ '^\d+$' THEN f.payment_terms::integer
        ELSE NULL
    END AS payment_terms,  -- Convert text to integer if numeric
    COALESCE(f.commission_rate, 0)::numeric(5,2),
    COALESCE(f.commission_discount_rate, 0)::numeric(5,2),
    COALESCE(f.overall_discount_rate, 0)::numeric(5,2),
    f.additional_information,
    f.freight_terms,
    f.external_payment_terms,
    f.published,
    f.freight_discount_type,
    f.creation_type,
    f.created_by,
    COALESCE(f.entry_date, now())
FROM core.factories f
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
    creation_type = EXCLUDED.creation_type;
