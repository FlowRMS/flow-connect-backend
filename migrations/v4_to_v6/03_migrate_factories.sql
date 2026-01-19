-- Migration: Factories from v4 (public.factories) to v6 (pycore.factories)
-- Run order: 03
-- Dependencies: 01_migrate_users.sql

-- v4 schema: public.factories (factory_id, account_number, base_commission, commission_discount, discount_type,
--            email, freight_terms, overall_discount, payment_terms, pays_shipping, phone, ship_time, status,
--            title, commission_payment_time, projected_ship_time, uuid, lead_time, additional_information,
--            external_payment_terms, alias, create_date, created_by, creation_type, draft, inside_rep_id)
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
    f.uuid,
    f.title,
    f.account_number,
    f.email,
    f.phone,
    NULL,  -- logo_id not in v4
    CASE
        WHEN f.lead_time ~ '^\d+$' THEN f.lead_time::integer
        ELSE NULL
    END AS lead_time,
    CASE
        WHEN f.payment_terms ~ '^\d+$' THEN f.payment_terms::integer
        ELSE NULL
    END AS payment_terms,
    COALESCE(f.base_commission, 0)::numeric(5,2),
    COALESCE(f.commission_discount, 0)::numeric(5,2),
    COALESCE(f.overall_discount, 0)::numeric(5,2),
    f.additional_information,
    f.freight_terms,
    f.external_payment_terms,
    COALESCE(f.status, true),  -- Map status to published
    f.discount_type,  -- Map to freight_discount_type
    f.creation_type,
    f.created_by,
    COALESCE(f.create_date, now())
FROM public.factories f
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
