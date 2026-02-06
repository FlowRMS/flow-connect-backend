# Plan Workflow

This document defines the workflow for creating, executing, and completing plans.

---

## Prerequisites

**CRITICAL**: Before starting any plan work, you MUST read:
- [`docs/methodologies/tdd-standards.md`](tdd-standards.md) - TDD methodology (Red-Green-Refactor cycle)
- [`docs/methodologies/backend-standards.md`](backend-standards.md) - Python/SQLAlchemy/GraphQL coding standards
- [`docs/methodologies/workflow-common.md`](workflow-common.md) - Git, execution, and review standards

Do NOT proceed with implementation without reading these standards first.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Plan Creation](#plan-creation)
- [Git Commit Workflow](#git-commit-workflow)
- [Plan Document Standards](#plan-document-standards)
  - [Design Decisions (Optional)](#design-decisions-optional)
  - [Database Model Documentation](#database-model-documentation)
- [Plan Status Values](#plan-status-values)
- [Status Workflow (Key Phrases)](#status-workflow-key-phrases)
- [Execution Rules](#execution-rules)

**Document block order**: See [Document Block Structure](workflow-common.md#document-block-structure) for the mandatory block order that all plan documents must follow.

---

## Plan Creation

Plans can be created from a Linear task or from a prompt. See [Creation Flows](workflow-common.md#creation-flows) for the two supported flows and [Quick Document Creation](workflow-common.md#quick-document-creation-preserve-context) for the early-creation pattern.

---

## Git Commit Workflow

See [Git Workflow Standards](workflow-common.md#git-workflow-standards) for commit process details and examples.

### Plan-Specific Conventions

- **Branch naming**: `feature/[short-name-related-to-plan]` (keep it concise, not the full plan title)

### When to Commit

See [Commit Policy](workflow-common.md#commit-policy) for the full list of commit points. Plan-specific commit messages are listed in [Commit Message Format](#commit-message-format) below.

### Commit Message Format

| # | Commit Point | Message Format |
|---|-------------|----------------|
| 1 | Approved | `[Prefix] - Add plan` |
| 2 | Phase complete | `[Prefix] - Phase N - [Brief description]` |
| 3 | Verification | `[Prefix] - Verification complete` |
| 4 | CDT entry | `[Prefix] - CDT BF-1 - [Brief description]` |
| 5 | Review | `[Prefix] - Review complete` |
| 6 | CPR entry | `[Prefix] - PR review CH-1 - [Brief description]` |
| 7 | CPR re-verification | `[Prefix] - PR review - Verification complete` |
| 8 | CPR re-review | `[Prefix] - PR review - Review complete` |
| 9 | Complete | `[Prefix] - Complete` |

---

## Plan Document Standards

### Location & Naming

- **All plans must be created in `./docs/plans/YYYY-MM/`** (organized by month)
- **Naming convention**: `YYYY-MM-DD-NN-kebab-case-title.md` where `NN` is an incremental number
- **Folder structure**:
  ```
  docs/plans/
  ├── 2026-01/
  │   ├── 2026-01-13-01-remote-manufacturer-directory.md
  │   └── ...
  ├── 2026-02/
  │   └── ...
  ```
- Create new month folders as needed
- NEVER use the system's default `.claude/plans/` directory

### Plan Header Format

```markdown
- **Status**: 🟡 In Progress - Phase X
- **Linear Task**: [TASK-123](https://linear.app/...)  <!-- Link to Linear task -->
- **Created**: YYYY-MM-DD HH:MM TZ  <!-- Use system time: `date "+%Y-%m-%d %H:%M %Z"` -->
- **Approved**: YYYY-MM-DD HH:MM TZ  <!-- Add when status changes to 🔵 Approved -->
- **Finished**: YYYY-MM-DD HH:MM TZ  <!-- Add when status changes to 🟦 Complete -->
- **PR**: [#123](https://github.com/...)  <!-- Add when status changes to 🟤 PR Ready -->
- **Commit Prefix**: XYZ  <!-- Prefix for all commits related to this plan -->
```

### Plan Structure Requirements

- **Table of Contents** - Add a simple TOC after the status/created section with links to each phase
- **Link to files after creation** - When a file is created/modified, update the plan to use clickable relative links: `**File**: [\`path/to/file.py\`](../../path/to/file.py)`. Only add links after the file exists.
- **Phase formatting**:
  - Add a brief description under each phase title (one line explaining the phase purpose)
  - Add ✅ icon to completed step headers (e.g., `### 1.1 GREEN: Create model ✅`)
- **Update plan documents when completing each step**: (1) Add ✅ to the step header, and (2) Update the **Status** field at the top of the document
- **Commit message format**: `[Commit Prefix] - [Phase] - [Message]`
  - Example: `Manufacturer Search Changes - Phase 1 - Make active filter nullable`
  - This format groups commits by plan in git history (`git log --grep="Manufacturer Search"`)

### Design Decisions (Optional)

When a plan involves architectural choices or design trade-offs discussed during planning, document them in a **Design Decisions** section between Overview and Phases.

**Format**:
```markdown
## Design Decisions

### DD-1: Short title for the decision

**Decision**: The chosen approach.

- Bullet points explaining rationale
- Why this was chosen over alternatives
- Any future considerations

### DD-2: Another decision

**Decision**: The chosen approach.

- Rationale...
```

**Guidelines**:
- Use `DD-N:` prefix for each decision (DD = Design Decision)
- Keep the title concise - the decision itself provides detail
- Don't include rejected alternatives in the final document (those were part of planning discussion)
- Include rationale and any future considerations

**Example**: See [`docs/plans/2026-01-26-02-rep-firms.md`](../plans/2026-01-26-02-rep-firms.md) for a complete example with multiple design decisions.

### Database Model Documentation

When documenting database models in plans, use the following table format for easy review:

```markdown
| | **public.table_name** | |
|-----|------|-------|
| **Column** | **Type** | **Constraints** |
| `id` | `UUID` | PK |
| `org_id` | `UUID` | FK → `organizations`, NOT NULL |
| `name` | `String(100)` | NOT NULL, UNIQUE |
| `status` | `MyStatusEnum` | NOT NULL, DEFAULT `active` |
| `created_at` | `DateTime` | NOT NULL |
| | **Indexes** | |
| | `ix_table_name_org_id` | `org_id` |
| | `ix_table_name_status` | `status` |
| | **Constraints** | |
| | `uq_table_name_org_name` | UNIQUE(`org_id`, `name`) |
```

**Format rules:**
- **Header row**: Empty first cell, schema.table_name in bold (e.g., `public.table_name`), empty third cell
- **Columns**: Column name, SQLAlchemy type, constraints (PK, FK, NOT NULL, UNIQUE, DEFAULT)
- **Indexes section**: List index name and columns
- **Constraints section**: Compound constraints (unique, check) - only if applicable
- **FK format**: `FK → target_table` (use arrow →)

---

## Plan Status Values

Use these standardized statuses:

| Status | Description | Trigger |
|--------|-------------|---------|
| 🔴 New | Initial state when plan is first created | - |
| 🟣 Under Review | User gave feedback, questions, or suggestions | ANY feedback on plan |
| 🔵 Approved | Plan approved, ready for execution | **"Approve the plan"** |
| 🟡 In Progress - Phase X | Implementation phase in progress | **"Implement the plan"** / **"Go to next phase"** |
| 🟡 In Progress - Verification | Manual testing in progress | **"Go to next phase"** (after last phase) |
| 🟠 Blocked | Execution blocked by external factor | - |
| 🟢 Steps Done | All steps completed (implementation + verification) | Verification complete |
| 🔍 Reviewing | Pre-PR review in progress | **"Review changes"** |
| 🟤 PR Ready | PR created, awaiting merge | **"Ready to PR"** |
| 🟡 In Progress - PR Changes | Addressing human PR review feedback | **"Address PR review"** |
| 🟦 Complete | Plan fully complete | **"Complete the plan"** |

---

## Status Workflow (Key Phrases)

These status transitions require explicit user approval with the specified key phrases:

| From | To | Key Phrase | Actions |
|------|-----|------------|---------|
| 🟣 Under Review | 🔵 Approved | **"Approve the plan"** | Add **Approved** date, create branch, commit plan |
| 🔵 Approved | 🟡 In Progress - Phase 1 | **"Implement the plan"** | Begin executing Phase 1 |
| 🟡 In Progress - Phase X | 🟡 In Progress - Phase X+1 | **"Go to next phase"** | Commit current phase changes, then start next phase |
| 🟡 In Progress - Phase N (last) | 🟡 In Progress - Verification | **"Go to next phase"** | Commit last phase, begin manual testing |
| 🟡 In Progress - Verification | 🟢 Steps Done | (automatic) | When verification completes |
| 🟢 Steps Done | 🔍 Reviewing | **"Review changes"** | Commit uncommitted changes, perform pre-PR review |
| 🔍 Reviewing | 🟤 PR Ready | **"Ready to PR"** | Push changes, create PR, add **PR** link to header |
| 🟤 PR Ready | 🟡 In Progress - PR Changes | **"Address PR review"** | Begin PR feedback changes |
| 🟡 In Progress - PR Changes | 🟤 PR Ready | (automatic) | Changes done, re-verify, re-review, push |
| 🟤 PR Ready | 🟦 Complete | **"Complete the plan"** | Add **Finished** date, fill Results table, commit, push |

**IMPORTANT**: Do NOT assume approval from phrases like "looks good", "proceed", or "start phase 1". Always wait for the exact key phrase.

**⚠️ MERGE ORDER**: Complete the plan FIRST, then merge the PR. This ensures the finalized plan document is included in the merge.

**⚠️ PR REVIEW CYCLE**: After "Ready to PR", the reviewer may request changes. Use **"Address PR review"** to handle this — it triggers an automatic cycle of changes → re-verification → re-review → push.

### When user says "Approve the plan"

1. Update status to 🔵 Approved and add **Approved** date
2. Create feature branch from main: `git checkout main && git pull && git checkout -b feature/[name]`
3. Make initial commit with the plan document
4. Wait for user to say **"Implement the plan"** before beginning execution

### When user says "Implement the plan"

1. Update status to 🟡 In Progress - Phase 1
2. Begin executing Phase 1

### When user says "Go to next phase"

1. Commit the current phase changes
2. If there are more implementation phases:
   - Update status to 🟡 In Progress - Phase X+1
   - Begin executing the next phase
3. If the last implementation phase was just completed:
   - Update status to 🟡 In Progress - Verification
   - Begin manual testing using the [Verification](workflow-common.md#verification) block
   - When verification completes:
     - Commit: `[Prefix] - Verification complete`
     - Update status to 🟢 Steps Done
   - **STOP** and wait for user to say **"Review changes"**

### When user says "Review changes"

1. **Commit any uncommitted changes** - ensure all prior work is committed before review
2. Update status to 🔍 Reviewing
3. Perform a review using the [Review Checklist](workflow-common.md#review-checklist)
4. Present findings to the user:
   - If concerns or changes are identified, **discuss them first** - do NOT apply changes directly
   - Wait for user feedback and resolution
5. After discussion is complete (or if no concerns):
   - Commit: `[Prefix] - Review complete`
   - Wait for user to say **"Ready to PR"**

### When user says "Ready to PR"

1. Update status to 🟤 PR Ready
2. Push changes to remote: `git push -u origin [branch-name]`
3. Create PR with the following format:

```
Title: [Same title as the plan document]

Body:
# Summary

[Brief overview of what the plan accomplishes]

**Task**: [Linear task title](Linear task link)

### Breaking Changes          <!-- only when applicable, omit otherwise -->
- Description of breaking change and impact

## Details

### Documents
1. **A** **`docs/plans/YYYY-MM-DD-NN-plan-name.md`** - Plan document

### DB Schema / Migrations
1. **A** `alembic/versions/YYYYMMDD_migration_name.py` - Description

### GraphQL Schema
1. **M** `schema.graphql` - Description of schema changes

### App Changes
1. **A** `app/path/to/new_file.py` - Description
2. **M** `app/path/to/modified_file.py` - Description

### Tests
1. **A** `tests/path/to/test_file.py` - Description
```

**Details section rules**:
- Group files by category: **Documents**, **DB Schema / Migrations**, **App Changes**, **Tests**
- Each category is a `### Heading` with a numbered list below
- Each line: **Bold** Git-style status (`A` = Added, `M` = Modified, `D` = Deleted) + file path + short one-line description
- The plan document file path must be in **bold**
- Omit categories that have no files (e.g., if no migrations, skip that section)
- **GraphQL Schema** section: Only include when `schema.graphql` is modified

4. **Link PR to Linear task** - See [PR to Linear Linking](workflow-common.md#pr-to-linear-linking)
5. Add the **PR** link to the plan header (do NOT commit yet - wait for "Complete the plan")
6. **Provide the GitHub PR link to the user** (e.g., "PR created: https://github.com/...")
7. **IMPORTANT**: Tell the user: `Say "Complete the plan" to finalize the plan document. After that, merge the PR.`

**⚠️ CRITICAL**: The next step is "Complete the plan", NOT merging the PR. The plan must be finalized BEFORE merging so the completed document is included in the merge.

### When user says "Address PR review"

1. Update status to 🟡 In Progress - PR Changes
2. For each requested change:
   a. Implement the fix following TDD standards
   b. Document in the [Changes after PR Review](workflow-common.md#changes-after-pr-review) section
   c. Update the [Files Changed](workflow-common.md#files-changed) table (use `CPR` as the Phase value)
   d. Run `task all` to verify all checks pass
   e. Commit: `[Prefix] - PR review CH-N - [description]`
3. **Automatically** re-execute [Verification](workflow-common.md#verification) — commit: `[Prefix] - PR review - Verification complete`
4. **Automatically** re-execute [Review](workflow-common.md#review-section) — commit: `[Prefix] - PR review - Review complete`
5. Push all commits to remote
6. Update status to 🟤 PR Ready
7. Notify the user that PR changes have been pushed

**Note**: This cycle can repeat if the reviewer has additional feedback.

### When user says "Complete the plan"

**IMPORTANT**: Complete the plan BEFORE merging the PR, so the finalized document is included in the merge.

1. Update status to 🟦 Complete and add **Finished** date
2. Fill in the Results table with actual values (Duration, Files Modified, Tests Added)
3. Commit and push the final plan document changes (status, PR link, Finished date, Results)

---

## Execution Rules

See [Execution Rules](workflow-common.md#execution-rules) for common standards (summaries, commit suggestions).

### After Creating a Plan

- Do NOT auto-call ExitPlanMode
- Say "The plan is ready for review" and provide the path to the plan document
- Wait for the user to explicitly say **"Approve the plan"**
- Never assume approval from other phrases or implicit signals

### Phase-by-Phase Execution

**CRITICAL**: Plans must be executed PHASE BY PHASE:
- Complete ONE phase, show the result
- **STOP AND WAIT for explicit user confirmation** before proceeding to the next phase
- Do NOT execute multiple phases at once unless the user explicitly says something like "complete all phases" or "do phases 3, 4, and 5"
- When user says "continue with phase X", ONLY do phase X and then STOP
- After the last implementation phase, "Go to next phase" transitions to the Verification block (not another phase)

### Phase Transition Rule (Context Restoration)

**⚠️ BLOCKING RULE**: After completing a phase, you MUST wait for the user to say **"Go to next phase"** before proceeding.

This rule is especially critical when **resuming from a compacted/summarized conversation**:
- Even if the summary says "Phase X is next" or "continue with Phase X", do NOT auto-proceed
- Even if instructed to "continue without asking questions", this rule still applies
- After completing any phase, ALWAYS ask: "Phase X complete. Ready for Phase Y when you say 'Go to next phase'."
- The user's explicit **"Go to next phase"** is the ONLY trigger to proceed

**Why this matters**: During conversation compaction, context about workflow rules may be summarized but not enforced. This rule ensures phase transitions always require explicit approval regardless of conversation state.
