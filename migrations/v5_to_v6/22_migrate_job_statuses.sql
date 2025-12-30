-- Migration: Job Statuses for v6 (pycrm.job_statuses)
-- Run order: 22
-- Dependencies: None

-- v5 doesn't have a job_statuses table, but crm.jobs has a status varchar field
-- We need to create status records based on unique statuses in the v5 jobs table

-- Insert unique job statuses from v5 jobs
INSERT INTO pycrm.job_statuses (
    id,
    name
)
SELECT
    gen_random_uuid(),
    DISTINCT j.status
FROM crm.jobs j
WHERE j.status IS NOT NULL
ON CONFLICT DO NOTHING;

-- If no statuses exist, create default ones
INSERT INTO pycrm.job_statuses (id, name)
SELECT gen_random_uuid(), 'Open'
WHERE NOT EXISTS (SELECT 1 FROM pycrm.job_statuses WHERE name = 'Open');

INSERT INTO pycrm.job_statuses (id, name)
SELECT gen_random_uuid(), 'In Progress'
WHERE NOT EXISTS (SELECT 1 FROM pycrm.job_statuses WHERE name = 'In Progress');

INSERT INTO pycrm.job_statuses (id, name)
SELECT gen_random_uuid(), 'Closed'
WHERE NOT EXISTS (SELECT 1 FROM pycrm.job_statuses WHERE name = 'Closed');
