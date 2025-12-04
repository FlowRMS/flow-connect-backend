-- Migration script: core.notes -> pycrm.notes + pycrm.link_relations
--
-- Old NoteEntityTypeEnum (core.notes.entity_type):
--   QUOTE=0, ORDER=1, FACTORY=2, CUSTOMER=3, PRODUCT=4,
--   CHECK=5, INVOICE=6, JOB=7, PRE_OPPORTUNITY=8, CONTACT=9
--
-- New EntityType (pycrm.link_relations):
--   JOB=1, TASK=2, CONTACT=3, COMPANY=4, NOTE=5,
--   PRE_OPPORTUNITY=6, QUOTE=7, ORDER=8, INVOICE=9, CHECK=10

BEGIN;

-- Step 1: Insert notes from core.notes into pycrm.notes
-- Mapping: title defaults to empty string if null, tags/mentions are new fields (null)
INSERT INTO pycrm.notes (id, created_at, created_by_id, title, content, tags, mentions)
SELECT
    n.id,
    n.entry_date AT TIME ZONE 'UTC' AS created_at,
    n.created_by AS created_by_id,
    COALESCE(n.title, '') AS title,
    n.content,
    NULL AS tags,
    n.user_owner_ids AS mentions
FROM core.notes n
WHERE n.parent_id IS NULL  -- Only migrate top-level notes, not replies
ON CONFLICT (id) DO NOTHING;

-- Step 2: Create link_relations to associate notes with their source entities
-- This maps the old entity_type (smallint) to the new EntityType enum values
INSERT INTO pycrm.link_relations (id, created_at, created_by_id, source_entity_type, source_entity_id, target_entity_type, target_entity_id)
SELECT
    gen_random_uuid() AS id,
    n.entry_date AT TIME ZONE 'UTC' AS created_at,
    n.created_by AS created_by_id,
    5 AS source_entity_type,  -- NOTE = 5
    n.id AS source_entity_id,
    CASE n.entity_type
        WHEN 0 THEN 7   -- QUOTE -> QUOTE
        WHEN 1 THEN 8   -- ORDER -> ORDER
        WHEN 3 THEN 4   -- CUSTOMER -> COMPANY
        WHEN 5 THEN 10  -- CHECK -> CHECK
        WHEN 6 THEN 9   -- INVOICE -> INVOICE
        WHEN 7 THEN 1   -- JOB -> JOB
        WHEN 8 THEN 6   -- PRE_OPPORTUNITY -> PRE_OPPORTUNITY
        WHEN 9 THEN 3   -- CONTACT -> CONTACT
    END AS target_entity_type,
    n.source_id AS target_entity_id
FROM core.notes n
WHERE n.parent_id IS NULL  -- Only top-level notes
  AND n.entity_type IN (0, 1, 3, 5, 6, 7, 8, 9)  -- Exclude FACTORY(2) and PRODUCT(4) - no mapping
ON CONFLICT DO NOTHING;

-- Step 3: Migrate note replies to pycrm.note_conversations
INSERT INTO pycrm.note_conversations (id, created_at, created_by_id, note_id, content)
SELECT
    n.id,
    n.entry_date AT TIME ZONE 'UTC' AS created_at,
    n.created_by AS created_by_id,
    n.parent_id AS note_id,
    n.content
FROM core.notes n
WHERE n.parent_id IS NOT NULL  -- Only replies
  AND EXISTS (SELECT 1 FROM pycrm.notes pn WHERE pn.id = n.parent_id)  -- Parent exists in pycrm
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- Verification queries (run separately after migration)
-- SELECT COUNT(*) AS pycrm_notes_count FROM pycrm.notes;
-- SELECT COUNT(*) AS core_notes_count FROM core.notes WHERE parent_id IS NULL;
-- SELECT COUNT(*) AS link_relations_count FROM pycrm.link_relations WHERE source_entity_type = 5;
-- SELECT COUNT(*) AS conversations_count FROM pycrm.note_conversations;
-- SELECT COUNT(*) AS core_replies_count FROM core.notes WHERE parent_id IS NOT NULL;
