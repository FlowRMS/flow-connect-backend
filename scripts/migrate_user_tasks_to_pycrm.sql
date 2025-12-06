-- Migration script: user.tasks -> pycrm.tasks
--
-- Old status (varchar): 'notStarted', 'inProgress', 'completed', 'waitingOnOthers', 'deferred'
-- New TaskStatus (IntEnum): TODO=1, IN_PROGRESS=2, COMPLETED=3, CANCELLED=4
--
-- Old importance (varchar): 'low', 'normal', 'high'
-- New TaskPriority (IntEnum): LOW=1, NORMAL=2, URGENT=3, CRITICAL=4
--
-- Field mapping:
--   body -> description
--   user_id -> created_by_id
--   importance -> priority
--   due_at -> due_date (timestamp to date)
--   reminder_at -> reminder_date (timestamp to date)
--   categories (json) -> tags (array)
--
-- Dropped fields:
--   - is_reminder_on, completed_at, position, private, steps, updated_at

BEGIN;

-- Migrate tasks from user.tasks to pycrm.tasks
INSERT INTO pycrm.tasks (
    id, created_at, created_by_id, title, status, priority,
    description, assigned_to_id, due_date, reminder_date, tags
)
SELECT
    t.id,
    t.created_at AT TIME ZONE 'UTC' AS created_at,
    t.user_id AS created_by_id,
    t.title,
    CASE LOWER(t.status)
        WHEN 'notstarted' THEN 1      -- TODO
        WHEN 'inprogress' THEN 2      -- IN_PROGRESS
        WHEN 'completed' THEN 3       -- COMPLETED
        WHEN 'waitingonothers' THEN 2 -- IN_PROGRESS (closest match)
        WHEN 'deferred' THEN 4        -- CANCELLED (closest match)
        ELSE 1                        -- Default to TODO
    END AS status,
    CASE LOWER(t.importance)
        WHEN 'low' THEN 1     -- LOW
        WHEN 'normal' THEN 2  -- NORMAL
        WHEN 'high' THEN 3    -- URGENT
        ELSE 2                -- Default to NORMAL
    END AS priority,
    t.body AS description,
    NULL AS assigned_to_id,
    t.due_at::date AS due_date,
    t.reminder_at::date AS reminder_date,
    -- Convert categories JSON array to text array
    CASE
        WHEN t.categories IS NOT NULL AND t.categories::text != 'null'
        THEN ARRAY(SELECT jsonb_array_elements_text(t.categories::jsonb))
        ELSE NULL
    END AS tags
FROM "user".tasks t
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- Verification queries (run separately after migration)
-- SELECT COUNT(*) AS pycrm_tasks_count FROM pycrm.tasks;
-- SELECT COUNT(*) AS user_tasks_count FROM "user".tasks;
-- SELECT status, COUNT(*) FROM pycrm.tasks GROUP BY status;
-- SELECT priority, COUNT(*) FROM pycrm.tasks GROUP BY priority;
