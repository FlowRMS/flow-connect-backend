-- Migration: Quote Balances from v5 (crm.quote_balances) to v6 (pycrm.quote_balances)
-- Run order: 17
-- Dependencies: None

-- v5 schema: crm.quote_balances (id, total, quantity, commission_rate, commission,
--            commission_discount_rate, commission_discount, discount, discount_rate, subtotal)
-- v6 schema: pycrm.quote_balances (quantity, subtotal, total, commission, discount, discount_rate,
--            commission_rate, commission_discount, commission_discount_rate, id)

INSERT INTO pycrm.quote_balances (
    id,
    quantity,
    subtotal,
    total,
    commission,
    discount,
    discount_rate,
    commission_rate,
    commission_discount,
    commission_discount_rate
)
SELECT
    qb.id,
    COALESCE(qb.quantity, 0),
    COALESCE(qb.subtotal, 0),
    COALESCE(qb.total, 0),
    COALESCE(qb.commission, 0),
    COALESCE(qb.discount, 0),
    COALESCE(qb.discount_rate, 0),
    COALESCE(qb.commission_rate, 0),
    COALESCE(qb.commission_discount, 0),
    COALESCE(qb.commission_discount_rate, 0)
FROM crm.quote_balances qb
ON CONFLICT (id) DO UPDATE SET
    quantity = EXCLUDED.quantity,
    subtotal = EXCLUDED.subtotal,
    total = EXCLUDED.total,
    commission = EXCLUDED.commission,
    discount = EXCLUDED.discount,
    discount_rate = EXCLUDED.discount_rate,
    commission_rate = EXCLUDED.commission_rate,
    commission_discount = EXCLUDED.commission_discount,
    commission_discount_rate = EXCLUDED.commission_discount_rate;
