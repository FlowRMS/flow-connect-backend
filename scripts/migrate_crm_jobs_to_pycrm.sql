-- Migration script: crm.jobs -> pycrm.jobs
--
-- Old crm.jobs schema:
--   id, entry_date, created_by, creation_type, user_owner_ids, status (varchar),
--   is_used, job_name, start_date, end_date, description, requester_id, job_owner_id
--
-- New pycrm.jobs schema:
--   id, created_at, created_by_id, job_name, status_id (FK to job_statuses),
--   start_date, end_date, description, job_type, structural_details,
--   structural_information, additional_information, requester_id, job_owner_id, tags
--
-- New pycrm.job_statuses: BID, BUY, COMPLETE

BEGIN;

-- Step 1: Ensure all status values from crm.jobs exist in pycrm.job_statuses
-- Insert any missing statuses (case-insensitive match)
INSERT INTO pycrm.job_statuses (id, name)
SELECT gen_random_uuid(), UPPER(TRIM(j.status))
FROM (SELECT DISTINCT UPPER(TRIM(status)) AS status FROM crm.jobs) j
WHERE NOT EXISTS (
    SELECT 1 FROM pycrm.job_statuses js
    WHERE UPPER(js.name) = UPPER(TRIM(j.status))
)
ON CONFLICT (name) DO NOTHING;

-- Step 2: Migrate jobs from crm.jobs to pycrm.jobs
INSERT INTO pycrm.jobs (
    id,
    created_at,
    created_by_id,
    job_name,
    status_id,
    start_date,
    end_date,
    description,
    job_type,
    structural_details,
    structural_information,
    additional_information,
    requester_id,
    job_owner_id,
    tags
)
SELECT
    j.id,
    j.entry_date AT TIME ZONE 'UTC' AS created_at,
    j.created_by AS created_by_id,
    j.job_name,
    js.id AS status_id,
    j.start_date,
    j.end_date,
    j.description,
    NULL AS job_type,
    NULL AS structural_details,
    NULL AS structural_information,
    NULL AS additional_information,
    j.requester_id,
    j.job_owner_id,
    NULL AS tags
FROM crm.jobs j
JOIN pycrm.job_statuses js ON UPPER(js.name) = UPPER(TRIM(j.status))
ON CONFLICT (id) DO NOTHING;

-- Step 3: Create link_relations for jobs linked to quotes
-- EntityType: JOB=1, QUOTE=7
INSERT INTO pycrm.link_relations (id, created_at, created_by_id, source_entity_type, source_entity_id, target_entity_type, target_entity_id)
SELECT
    gen_random_uuid() AS id,
    q.entry_date AT TIME ZONE 'UTC' AS created_at,
    q.created_by AS created_by_id,
    1 AS source_entity_type,  -- JOB = 1
    q.job_id AS source_entity_id,
    7 AS target_entity_type,  -- QUOTE = 7
    q.id AS target_entity_id
FROM crm.quotes q
WHERE q.job_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM pycrm.jobs j WHERE j.id = q.job_id)
ON CONFLICT DO NOTHING;

-- Step 4: Create link_relations for jobs linked to orders
-- EntityType: JOB=1, ORDER=8
INSERT INTO pycrm.link_relations (id, created_at, created_by_id, source_entity_type, source_entity_id, target_entity_type, target_entity_id)
SELECT
    gen_random_uuid() AS id,
    o.entry_date AT TIME ZONE 'UTC' AS created_at,
    o.created_by AS created_by_id,
    1 AS source_entity_type,  -- JOB = 1
    o.job_id AS source_entity_id,
    8 AS target_entity_type,  -- ORDER = 8
    o.id AS target_entity_id
FROM commission.orders o
WHERE o.job_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM pycrm.jobs j WHERE j.id = o.job_id)
ON CONFLICT DO NOTHING;

COMMIT;

-- Verification queries (run separately after migration)
-- SELECT COUNT(*) AS pycrm_jobs_count FROM pycrm.jobs;
-- SELECT COUNT(*) AS crm_jobs_count FROM crm.jobs;
-- SELECT js.name, COUNT(j.id) AS job_count
-- FROM pycrm.jobs j
-- JOIN pycrm.job_statuses js ON j.status_id = js.id
-- GROUP BY js.name;
-- SELECT COUNT(*) AS job_quote_links FROM pycrm.link_relations WHERE source_entity_type = 1 AND target_entity_type = 7;
-- SELECT COUNT(*) AS job_order_links FROM pycrm.link_relations WHERE source_entity_type = 1 AND target_entity_type = 8;
-- SELECT COUNT(*) AS quotes_with_job FROM crm.quotes WHERE job_id IS NOT NULL;
-- SELECT COUNT(*) AS orders_with_job FROM commission.orders WHERE job_id IS NOT NULL;
