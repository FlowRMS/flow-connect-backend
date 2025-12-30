-- Migration: Pre-Opportunity Balances from v5 (crm.pre_opportunity_balances) to v6 (pycrm.pre_opportunity_balances)
-- Run order: 24
-- Dependencies: None

-- v5 schema: crm.pre_opportunity_balances (id, subtotal, total, quantity, commission_rate, commission,
--            commission_discount_rate, commission_discount, discount, discount_rate)
-- v6 schema: pycrm.pre_opportunity_balances (subtotal, total, quantity, discount, discount_rate, id)

-- Note: v6 has fewer fields - no commission-related columns

INSERT INTO pycrm.pre_opportunity_balances (
    id,
    subtotal,
    total,
    quantity,
    discount,
    discount_rate
)
SELECT
    pob.id,
    COALESCE(pob.subtotal, 0),
    COALESCE(pob.total, 0),
    COALESCE(pob.quantity, 0),
    COALESCE(pob.discount, 0),
    COALESCE(pob.discount_rate, 0)
FROM crm.pre_opportunity_balances pob
ON CONFLICT (id) DO UPDATE SET
    subtotal = EXCLUDED.subtotal,
    total = EXCLUDED.total,
    quantity = EXCLUDED.quantity,
    discount = EXCLUDED.discount,
    discount_rate = EXCLUDED.discount_rate;
