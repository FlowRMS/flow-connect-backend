# Rouzer Data Fix: Contact-Customer Bidirectional Display

**Date:** 2026-01-28
**Status:** Pending
**Type:** Frontend Fix (not database)

## Issue Description

When viewing a Contact (e.g., "Dan Howell"), related Customers (e.g., "Viking Electric Supply - Mpls") are not displayed, even though the link exists in the database. However, when viewing the Customer, the Contact is visible.

## Root Cause Analysis

| Layer | Status | Details |
|-------|--------|---------|
| **Database** | OK | Links exist: Contact (type 3) -> Customer (type 12) |
| **Backend** | OK | `ContactRelatedEntitiesStrategy` returns `customers` (line 105, 123) |
| **GraphQL Query** | OK | Requests `customers` field in `GET_RELATED_ENTITIES` |
| **Frontend Component** | BUG | `ContactRelatedEntities.tsx` only displays `companies`, ignores `customers` |

### Evidence

**Database Query (Rouzer tenant):**
```sql
-- Dan Howell contact ID: a2c64d7d-73ff-42a1-a360-96473576eebd
-- Viking Electric Supply - Mpls customer ID: 5e7f37fb-623b-4d9b-9a6a-ec0272cc5d47

SELECT * FROM pycrm.link_relations
WHERE source_entity_id = 'a2c64d7d-73ff-42a1-a360-96473576eebd'
  AND target_entity_id = '5e7f37fb-623b-4d9b-9a6a-ec0272cc5d47';
-- Returns 2 records (duplicate links, but data exists)
```

**Frontend Bug Location:**
- File: `flow-crm/components/contacts/detail/ContactRelatedEntities.tsx`
- Line 240: `const companies = relatedEntities?.companies || [];`
- Problem: Never reads `relatedEntities?.customers`

## Fix Required

Update `ContactRelatedEntities.tsx` to display linked customers:

### Option 1: Add Separate "Related Customers" Section
Add a new section similar to "Associated Company" that displays linked customers.

### Option 2: Merge Companies and Customers
Combine both entity types into a single "Related Organizations" section.

## Files to Modify

1. `flow-crm/components/contacts/detail/ContactRelatedEntities.tsx`
   - Add state for customers: `const customers = relatedEntities?.customers || [];`
   - Add UI section to display customers
   - Add unlink functionality for customers

2. Optionally update `flow-crm/docs/claude/contacts.claude.md` with the new feature

## Additional Data Quality Notes

### Duplicate Links Found
There are 7,855 duplicate Contact -> Customer link pairs in the database:
```sql
SELECT COUNT(*) FROM (
  SELECT source_entity_id, target_entity_id
  FROM pycrm.link_relations
  WHERE source_entity_type = 3 AND target_entity_type = 12
  GROUP BY source_entity_id, target_entity_id
  HAVING COUNT(*) > 1
) dups;
-- Returns: 7855
```

Consider running a cleanup script to remove duplicate links (keep oldest):
```sql
DELETE FROM pycrm.link_relations a
USING pycrm.link_relations b
WHERE a.source_entity_type = 3 AND a.target_entity_type = 12
  AND a.source_entity_id = b.source_entity_id
  AND a.target_entity_id = b.target_entity_id
  AND a.created_at > b.created_at;
```

## Entity Type Reference

| Type | Entity |
|------|--------|
| 1 | Factory |
| 2 | Job |
| 3 | Contact |
| 4 | Product |
| 5 | Quote |
| 6 | Order |
| 11 | Pre-Opportunity |
| 12 | Customer |
