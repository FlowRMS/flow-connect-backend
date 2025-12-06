-- Migration script: core.factories + core.customers -> pycrm.companies
--                   core.contacts -> pycrm.contacts
--
-- CompanyType (IntEnum): CUSTOMER=1, MANUFACTURER=2
--
-- Field mapping for factories -> companies:
--   title -> name
--   phone -> phone
--   company_source_type = 2 (MANUFACTURER)
--
-- Field mapping for customers -> companies:
--   company_name -> name
--   contact_number -> phone
--   parent_id -> parent_company_id
--   company_source_type = 1 (CUSTOMER)
--
-- Field mapping for contacts:
--   firstname -> first_name
--   lastname -> last_name
--   title -> role
--   source_id -> company_id (based on entity_type: 2=FACTORY, 3=CUSTOMER)
--
-- Old contact entity_type values:
--   QUOTE=0, ORDER=1, FACTORY=2, CUSTOMER=3, PRODUCT=4, CHECK=5, INVOICE=6, JOB=7

BEGIN;

-- Step 1: Migrate factories to companies (as MANUFACTURER type)
INSERT INTO pycrm.companies (
    id, created_at, created_by_id, name, company_source_type,
    website, phone, tags, parent_company_id
)
SELECT
    f.id,
    f.entry_date AT TIME ZONE 'UTC' AS created_at,
    f.created_by AS created_by_id,
    f.title AS name,
    2 AS company_source_type,  -- MANUFACTURER = 2
    f.logo_url AS website,
    f.phone,
    NULL AS tags,
    NULL AS parent_company_id
FROM core.factories f
ON CONFLICT (id) DO NOTHING;

-- Step 2: Migrate customers to companies (as CUSTOMER type)
-- First pass: customers without parent (or parent not yet migrated)
INSERT INTO pycrm.companies (
    id, created_at, created_by_id, name, company_source_type,
    website, phone, tags, parent_company_id
)
SELECT
    c.id,
    c.entry_date AT TIME ZONE 'UTC' AS created_at,
    c.created_by AS created_by_id,
    c.company_name AS name,
    1 AS company_source_type,  -- CUSTOMER = 1
    c.logo_url AS website,
    c.contact_number AS phone,
    NULL AS tags,
    c.parent_id AS parent_company_id
FROM core.customers c
ON CONFLICT (id) DO NOTHING;

-- Step 3: Migrate contacts linked to factories (entity_type = 2)
INSERT INTO pycrm.contacts (
    id, created_at, created_by_id, first_name, last_name,
    email, phone, role, territory, tags, notes, company_id
)
SELECT
    c.id,
    c.entry_date AT TIME ZONE 'UTC' AS created_at,
    c.created_by AS created_by_id,
    c.firstname AS first_name,
    c.lastname AS last_name,
    c.email,
    c.phone,
    NULLIF(c.title, '') AS role,
    NULL AS territory,
    NULL AS tags,
    NULL AS notes,
    c.source_id AS company_id
FROM core.contacts c
WHERE c.entity_type = 2  -- FACTORY
  AND c.source_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM pycrm.companies co WHERE co.id = c.source_id)
ON CONFLICT (id) DO NOTHING;

-- Step 4: Migrate contacts linked to customers (entity_type = 3)
INSERT INTO pycrm.contacts (
    id, created_at, created_by_id, first_name, last_name,
    email, phone, role, territory, tags, notes, company_id
)
SELECT
    c.id,
    c.entry_date AT TIME ZONE 'UTC' AS created_at,
    c.created_by AS created_by_id,
    c.firstname AS first_name,
    c.lastname AS last_name,
    c.email,
    c.phone,
    NULLIF(c.title, '') AS role,
    NULL AS territory,
    NULL AS tags,
    NULL AS notes,
    c.source_id AS company_id
FROM core.contacts c
WHERE c.entity_type = 3  -- CUSTOMER
  AND c.source_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM pycrm.companies co WHERE co.id = c.source_id)
ON CONFLICT (id) DO NOTHING;

-- Step 5: Migrate contacts without company association (other entity types or no source)
INSERT INTO pycrm.contacts (
    id, created_at, created_by_id, first_name, last_name,
    email, phone, role, territory, tags, notes, company_id
)
SELECT
    c.id,
    c.entry_date AT TIME ZONE 'UTC' AS created_at,
    c.created_by AS created_by_id,
    c.firstname AS first_name,
    c.lastname AS last_name,
    c.email,
    c.phone,
    NULLIF(c.title, '') AS role,
    NULL AS territory,
    NULL AS tags,
    NULL AS notes,
    NULL AS company_id
FROM core.contacts c
WHERE c.entity_type NOT IN (2, 3)  -- Not FACTORY or CUSTOMER
   OR c.source_id IS NULL
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- Verification queries (run separately after migration)
-- SELECT COUNT(*) AS pycrm_companies_count FROM pycrm.companies;
-- SELECT COUNT(*) AS core_factories_count FROM core.factories;
-- SELECT COUNT(*) AS core_customers_count FROM core.customers;
-- SELECT company_source_type, COUNT(*) FROM pycrm.companies GROUP BY company_source_type;
-- SELECT COUNT(*) AS pycrm_contacts_count FROM pycrm.contacts;
-- SELECT COUNT(*) AS core_contacts_count FROM core.contacts;
-- SELECT COUNT(*) AS contacts_with_company FROM pycrm.contacts WHERE company_id IS NOT NULL;
-- SELECT COUNT(*) AS contacts_without_company FROM pycrm.contacts WHERE company_id IS NULL;
