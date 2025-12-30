-- Migration: Jobs from v5 (crm.jobs) to v6 (pycrm.jobs)
-- Run order: 23
-- Dependencies: 01_migrate_users.sql, 22_migrate_job_statuses.sql

-- v5 schema: crm.jobs (id, entry_date, created_by, creation_type, user_owner_ids, status, is_used,
--            job_name, start_date, end_date, description, requester_id, job_owner_id, participant_ids)
-- v6 schema: pycrm.jobs (job_name, status_id, start_date, end_date, job_type, structural_details,
--            structural_information, additional_information, description, requester_id, job_owner_id,
--            tags, id, created_at, created_by_id)

INSERT INTO pycrm.jobs (
    id,
    job_name,
    status_id,
    start_date,
    end_date,
    job_type,
    structural_details,
    structural_information,
    additional_information,
    description,
    requester_id,
    job_owner_id,
    tags,
    created_at,
    created_by_id
)
SELECT
    j.id,
    j.job_name,
    (SELECT js.id FROM pycrm.job_statuses js WHERE js.name = j.status LIMIT 1),
    j.start_date,
    j.end_date,
    NULL,  -- job_type not in v5
    NULL,  -- structural_details not in v5
    NULL,  -- structural_information not in v5
    NULL,  -- additional_information not in v5
    j.description,
    j.requester_id,
    j.job_owner_id,
    NULL,  -- tags not in v5
    COALESCE(j.entry_date, now()),
    j.created_by
FROM crm.jobs j
ON CONFLICT (id) DO UPDATE SET
    job_name = EXCLUDED.job_name,
    status_id = EXCLUDED.status_id,
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    description = EXCLUDED.description,
    requester_id = EXCLUDED.requester_id,
    job_owner_id = EXCLUDED.job_owner_id;
