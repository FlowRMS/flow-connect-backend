-- Migration: Add overage and fixture_schedule fields to quote_details
-- Description: Support for Overage View feature in quotes

-- Add overage commission rate (calculated from product/factory settings)
ALTER TABLE pycrm.quote_details
ADD COLUMN IF NOT EXISTS overage_commission_rate DECIMAL(18, 6);

-- Add overage commission amount (overage_commission_rate * sell_total)
ALTER TABLE pycrm.quote_details
ADD COLUMN IF NOT EXISTS overage_commission DECIMAL(18, 6);

-- Add overage unit price (unit_price * (1 + overage_percent))
ALTER TABLE pycrm.quote_details
ADD COLUMN IF NOT EXISTS overage_unit_price DECIMAL(18, 6);

-- Add fixture schedule type for overage view (TYPE_A, TYPE_B, TYPE_C, TYPE_D, TYPE_E)
ALTER TABLE pycrm.quote_details
ADD COLUMN IF NOT EXISTS fixture_schedule VARCHAR(50);

-- Comments
COMMENT ON COLUMN pycrm.quote_details.overage_commission_rate IS 'Effective commission rate from product/factory overage settings';
COMMENT ON COLUMN pycrm.quote_details.overage_commission IS 'Calculated overage commission amount';
COMMENT ON COLUMN pycrm.quote_details.overage_unit_price IS 'Unit price including overage markup';
COMMENT ON COLUMN pycrm.quote_details.fixture_schedule IS 'Fixture schedule type (TYPE_A through TYPE_E) for overage view';
