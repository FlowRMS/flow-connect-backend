# Workflow Common Standards

This document contains shared standards for both plan and hotfix workflows.

---

## Table of Contents

- [Document Block Structure](#document-block-structure)
- [Creation Flows](#creation-flows)
  - [Flow A: From Linear Task](#flow-a-from-linear-task)
  - [Flow B: From Prompt](#flow-b-from-prompt)
- [Quick Document Creation (Preserve Context)](#quick-document-creation-preserve-context)
- [PR to Linear Linking](#pr-to-linear-linking)
- [Git Workflow Standards](#git-workflow-standards)
  - [Commit Policy](#commit-policy)
  - [Commit Before Changes](#commit-before-changes)
- [Execution Rules](#execution-rules)
- [Verification](#verification)
- [Changes During Testing](#changes-during-testing)
- [Review Checklist](#review-checklist)
- [Review Section](#review-section)
- [Changes after PR Review](#changes-after-pr-review)
- [GraphQL API Changes (Optional)](#graphql-api-changes-optional)
- [Breaking Changes](#breaking-changes)
- [Files Changed](#files-changed)
- [Results Table](#results-table)

---

## Document Block Structure

All plan and hotfix documents must follow this mandatory block order. Optional blocks are omitted when not applicable — do not add empty placeholders.

| # | Block | Required | Description |
|---|-------|----------|-------------|
| 1 | Overview | Yes | What the plan/hotfix accomplishes |
| 2 | Design Decisions | Optional | Architectural choices with rationale (DD-N prefix) |
| 3 | Phases | Yes | Implementation steps only (no verification) |
| 4 | Verification | Yes | Manual testing. Standalone, re-executable |
| 5 | Changes During Testing | Optional | Issues found during verification (BF/CH prefixes) |
| 6 | GraphQL API Changes | Optional | Schema changes when `schema.graphql` is modified |
| 7 | Review | Yes | Pre-PR review checklist. Re-executable |
| 8 | Changes after PR Review | Optional | Changes from human PR review (BF/CH/REC prefixes) |
| 9 | Files Changed | Yes | Cumulative file inventory |
| 10 | Results | Yes | Metrics — TBD until "Complete the plan/hotfix" |

---

## Creation Flows

Plans and hotfixes can be created in two ways.

**⚠️ CRITICAL**: Every plan and hotfix MUST have a Linear task. Flow A receives one from the user; Flow B requires creating one automatically. Never skip the Linear task creation step.

### Flow A: From Linear Task

The user provides a Linear task ID (e.g., `FLO-1504`).

1. **Read the task** via Linear MCP (`get_issue`)
2. **Create the document** using the task information:
   - Title derived from the task title
   - Description/Overview populated from the task description
   - `Linear Task` header field populated automatically with the task identifier and URL
3. **Update the Linear task status** - If the task status is "Todo", move it to "In Progress" via Linear MCP (`update_issue`). If it's already in another status, leave it unchanged.
4. Follow the [Quick Document Creation](#quick-document-creation-preserve-context) pattern

### Flow B: From Prompt

The user describes the work in conversation (no Linear task exists yet).

1. **Create the document** following the [Quick Document Creation](#quick-document-creation-preserve-context) pattern
2. **⚠️ Create a Linear task automatically** via Linear MCP (`create_issue`) — this step is **MANDATORY**, do NOT skip it:
   - **Team**: Flow Labs (default)
   - **Project**: Ask the user if not specified
   - **Title**: Same as the document title
   - **Description**: Brief summary from the document overview
   - **Status**: "In Progress" (set via `state` parameter)
   - **Assignee**: "me" (current authenticated user)
3. **Populate the `Linear Task` header** in the document with the newly created task identifier and URL

**IMPORTANT**: The Linear task is created when the document is first created (status 🔴 New), not when approved. This ensures the link exists early.

---

## Quick Document Creation (Preserve Context)

**CRITICAL**: Create the plan/hotfix document EARLY to preserve discussion context.

When the user requests a new plan or reports a bug:
1. **Create the document quickly** with at minimum:
   - Header (status, linear task, created date, commit prefix)
   - Overview/Problem section (even if incomplete)
   - Empty phases/solution or TBD placeholders
2. **Continue discussion** with the document as the living artifact
3. **Add details incrementally** as decisions are made during discussion
4. **Update status to 🟣 Under Review** (plans) when providing for user feedback

**Why this matters**: If the session is lost (timeout, crash, context compaction), all discussion is lost. The document serves as persistent storage for decisions made during planning. Create it early, update it often.

---

## PR to Linear Linking

When a PR is created during the "Ready to PR" step, the PR **must** be linked to the associated Linear task.

After running `gh pr create`:
1. **Update the Linear task** via MCP (`update_issue`) to add the PR URL as a link attachment
2. The link title should be the PR title (e.g., `PR #123: Plan Title`)

This applies to both plans and hotfixes. See the specific workflow documents for the full "Ready to PR" process.

**IMPORTANT**: Never change the Linear task status (e.g., moving to "Done"). The user manages task status transitions themselves. Claude's role is limited to: creating tasks, updating descriptions, and adding link attachments.

---

## Git Workflow Standards

Claude is responsible for creating commits. Follow these rules:

### Branch Management

- **Create a fresh branch from main** when a plan/hotfix is approved
- **Branch naming**: See specific workflow documents for naming conventions
- Always ensure you're on the correct branch before committing

### Commit Policy

Commits are made at **specific points only**. No other commits should be made outside of these points.

| # | Commit Point | Description |
|---|-------------|-------------|
| 1 | Approved | Initial commit with the plan/hotfix document |
| 2 | Phase complete | After each implementation phase (or implementation step for hotfixes) |
| 3 | Verification complete | After all 4 verification steps pass |
| 4 | CDT entry complete | After each Changes During Testing fix + re-verification |
| 5 | Review complete | After the review checklist is filled |
| 6 | CPR entry complete | After each Changes after PR Review fix |
| 7 | CPR re-verification | After re-executing verification post-CPR |
| 8 | CPR re-review | After re-executing review post-CPR |
| 9 | Complete | Final commit with status, dates, and Results |

**Rules**:
- Each commit uses a **single-line message** with the document's Commit Prefix
- See the plan/hotfix workflow documents for exact commit message formats
- **IMPORTANT**: After completing work, show the summary and suggest the commit message, then WAIT for user to approve before running `git commit`. Never auto-commit changes.

### Commit Before Changes

**⚠️ RULE**: After completing a phase/step, commit IMMEDIATELY before making any additional changes - even if the user requests modifications.

If the user requests changes after a phase is complete but before committing:
1. First commit the completed phase as-is
2. Then make the requested changes
3. Commit the changes as a separate commit (e.g., "Phase 3 - Refactor to individual parameters")

This ensures each phase has its own commit and changes are traceable.

### Commit Message Format

- **ONE LINE ONLY** - Never use multi-line commit messages (no bullet points, no paragraphs)
- **NO Co-Authored-By footer** - Do not add `Co-Authored-By: Claude...` or any other footer
- **NO HEREDOC** - Do not use `$(cat <<'EOF'...)` syntax for commit messages
- Keep the message concise but descriptive

### Commit Process

1. Run `git status` to verify changes
2. Stage relevant files with `git add`
3. Create commit with **single-line message only**: `git commit -m "[Commit Prefix] - [Phase/Action] - [Message]"`
4. Verify commit was successful with `git status`

### Examples

**BAD examples** (never do this):
```bash
# Multi-line with bullets - WRONG
git commit -m "$(cat <<'EOF'
Fix something

- Item 1
- Item 2

Co-Authored-By: Claude
EOF
)"

# Multi-line description - WRONG
git commit -m "Fix bug" -m "More details here"
```

**GOOD example**:
```bash
git commit -m "Organization Aliases - Phase 5 - Bugfixes from testing"
```

---

## Execution Rules

### After Creating a Document

- Do NOT auto-call ExitPlanMode
- Say "The [plan/hotfix] is ready for review" and provide the path to the document
- Wait for the user to explicitly approve
- Never assume approval from other phrases or implicit signals

### Don't Auto-Proceed Between Transitions

**⚠️ BLOCKING RULE**: After completing a phase or step, you MUST wait for the user's explicit approval before proceeding.

This rule is especially critical when **resuming from a compacted/summarized conversation**:
- Even if the summary says "Phase X is next" or "continue with Phase X", do NOT auto-proceed
- Even if instructed to "continue without asking questions", this rule still applies
- After completing any phase, ALWAYS ask: "Phase X complete. Ready for Phase Y when you say 'Go to next phase'."
- The user's explicit approval is the ONLY trigger to proceed

**Why this matters**: During conversation compaction, context about workflow rules may be summarized but not enforced. This rule ensures phase transitions always require explicit approval regardless of conversation state.

### After Completing Each Step

- Provide a short summary of changes
- List the modified/created/deleted files with their full paths

### After Completing Work

- Suggest a commit message using the document title or code format
- **Always include commit suggestion after changes** - Even if the commit message was already suggested earlier, always include it again in the final summary after any modifications

---

## Verification

Verification is a standalone block, not a phase. It is re-executed after Changes During Testing fixes and after Changes after PR Review changes.

### Steps

Verification has 4 sequential steps:

| # | Step | What it does |
|---|------|-------------|
| 1 | `task test` | Run pytest — all tests must pass |
| 2 | `task all` | Lint + typecheck + regenerate schema |
| 3 | Check `git diff schema.graphql` | Detect if schema was out of date (only meaningful when GraphQL types were modified) |
| 4 | Manual testing | Test against running server (see table format below) |

Document each step's result in the plan/hotfix:

```markdown
## Verification

### Step 1: Run tests
- `task test` — X tests passed ✅

### Step 2: Run task all
- `task all` — lint ✅, typecheck ✅, gql export ✅

### Step 3: Verify schema.graphql
- `git diff schema.graphql` — no changes ✅
  <!-- or: schema updated, committed ✅ -->
  <!-- or: N/A — no GraphQL types modified -->

### Step 4: Manual testing

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Test scenario | Expected result | |
```

### Step 3 Details

After `task all` regenerates `schema.graphql`, run `git diff schema.graphql`:
- **No diff** — schema was up to date ✅
- **Diff detected** — schema was stale. Review the changes, stage and commit the updated file
- **No GraphQL types modified** — mark as N/A

### Step 4: Manual Testing Standards

- **Never mark manual testing as passed when it fails** — even if the failure is due to an unrelated issue (environment, configuration, database), the step should NOT be marked as ✅
- **Document the blocker** — clearly describe what is blocking the test and why
- **Use ⏸️ for blocked steps** — mark blocked steps with ⏸️ (paused) instead of ✅
- **Resolve before proceeding** — manual testing issues should be investigated and resolved before moving to review

### Manual Testing Table Format

Define tests when writing the document (with empty Status), then fill in results during execution.

- **#**: Sequential number
- **Test**: What action to perform or scenario to verify
- **Expected**: The expected result or behavior
- **Status**: ✅ passed, ❌ failed, ⏸️ blocked. Add brief notes when relevant (e.g., `✅ Re-verified after CH-1`)

### Manual Testing Execution Approach

Run tests **one at a time** and update the table after each individual test. Do NOT batch-run all tests and then update statuses. This ensures:
- Progress is preserved if a session is interrupted
- Failures are caught and addressed immediately
- The user can see testing progress at any point

### Re-execution

When verification is re-executed (after Changes During Testing or Changes after PR Review), re-run all 4 steps and update results. Note when a manual test was re-verified (e.g., `✅ Re-verified after CH-1`).

---

## Changes During Testing

_Optional block. Only add when issues are discovered during verification._

When bug fixes or behavior changes are needed during verification, document them in this section. Each entry follows TDD (Red-Green-Refactor) for significant changes.

### Format

```markdown
## Changes During Testing

_Issues discovered and fixed during verification. Prefixes: BF = bugfix, CH = behavior change._

### BF-1: Short description ✅

**Problem**: What was wrong
**File**: [`path/to/file.py`](../../path/to/file.py)
**Fix**: What was done to fix it

### CH-1: Short description ✅

**Problem**: What needed to change
**Files**:
- [`file1.py`](../../file1.py) - Description
- [`file2.py`](../../file2.py) - Description
**Change**: What was changed
```

### Guidelines

- Use `BF-N` for bugfixes, `CH-N` for behavior changes
- Mark each entry ✅ when resolved
- For significant changes, add TDD sub-steps (e.g., `#### CH-1.1 RED`, `#### CH-1.2 GREEN`, `#### CH-1.3 REFACTOR`)
- After applying changes, re-execute Verification
- Commit after each entry is resolved (fix + re-verification)
- Do NOT embed fixes inside phase sections — keep them in this dedicated block

---

## Review Checklist

_This checklist is open for new items as needed._

- [ ] **Performance impact** - Do any changes affect performance negatively?
- [ ] **Effects on other features** - Could changes break or affect other parts of the system?
- [ ] **Code quality** - Verify against [backend-standards.md](backend-standards.md): file length ≤ 300 lines, no file header comments, type hints, architecture patterns (repository/service separation), proper DI, no anti-patterns
- [ ] **Potential bugs** - Are there edge cases, error handling gaps, or logic errors?
- [ ] **Commit policy** - All commit points present, single-line format, correct message patterns, no `Co-Authored-By` footer (`git log main..HEAD`)
- [ ] **Breaking changes** - Are there breaking changes to APIs, schemas, or contracts? If yes, documented in plan/hotfix and flagged for PR/Linear
- [ ] **Document updates** - Is there anything to add/modify/remove in the plan/hotfix document?

---

## Review Section

After completing the review checklist, document the results in a `## Review` section in the plan/hotfix document. The Review block is **re-executable** — it is re-run after Changes after PR Review changes.

### Placement

```
## Changes During Testing   ← optional
---
## GraphQL API Changes       ← optional
---
## Review                    ← review results go here
---
## Changes after PR Review   ← optional (populated after PR feedback)
---
## Files Changed             ← cumulative file inventory
---
## Results                   ← metrics (TBD until "Complete")
```

### Format

```markdown
## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns |
| 2 | Effects on other features | ✅ No negative effects |
| 3 | Code quality | ✅ Compliant with backend-standards.md |
| 4 | Potential bugs | ✅ None found |
| 5 | Commit policy | ✅ Compliant with commit policy |
| 6 | Breaking changes | ✅ None / ✅ Documented in GraphQL API Changes |
| 7 | Document updates | ✅ No changes needed |
```

### Guidelines

- One row per checklist item
- **Status column**: Use ✅ for passed checks. When a fix was needed, note it briefly (e.g., `✅ Fixed — removed Co-Authored-By from commit abc1234`)
- Add the `## Review` link to the document's Table of Contents

---

## GraphQL API Changes (Optional)

When a plan or hotfix modifies `schema.graphql`, document the changes in a `## GraphQL API Changes` section in the plan/hotfix document. This section is placed **between Changes During Testing and Review**.

### Format

```markdown
## GraphQL API Changes

_Breaking and non-breaking changes to the GraphQL schema._

| Change | Type | Detail |
|--------|------|--------|
| `TypeName.field`: `Type!` → `Type` | ⚠️ Breaking | Reason for the change |
| `query(...)`: `Type` → `Type!` | ✅ Non-breaking | Reason for the change |
```

### Guidelines

- One row per schema change
- **Type column**: Use `⚠️ Breaking` or `✅ Non-breaking`
- Breaking = clients may fail (removed fields, nullability changes from non-null to nullable, removed enum values)
- Non-breaking = clients won't fail (added fields, nullability changes from nullable to non-null, added enum values)
- Add the `## GraphQL API Changes` link to the document's Table of Contents
- Only add this section when `schema.graphql` is modified

---

## Changes after PR Review

_Optional block. Only add when changes are requested during human PR review._

When a human reviewer requests changes on the PR, document them here. This block is populated during the "Address PR review" workflow.

### Format

```markdown
## Changes after PR Review

_Changes from PR review. Prefixes: BF = bugfix, CH = behavior change, REC = recommendation._

### CH-1: Short description ✅

**Problem**: What the reviewer identified
**Review**: PR #123 review by [reviewer] (YYYY-MM-DD)
**Files**: [`path/to/file.py`](../../path/to/file.py)
**Change**: What was changed

### REC-1: Short description (deferred)

**Problem**: What the reviewer suggested
**Review**: PR #123 review by [reviewer] (YYYY-MM-DD)
**Files**: [`path/to/file.py`](../../path/to/file.py)
**Change**: Deferred — [reason]
```

### Guidelines

- Use `BF-N` for bugfixes, `CH-N` for behavior changes, `REC-N` for recommendations
- Mark implemented entries ✅, deferred entries with `(deferred)`
- Always include the `**Review**` field with PR number, reviewer name, and date
- `REC` entries are optional improvements — acknowledge but defer if not critical
- After applying changes, Verification and Review are automatically re-executed

---

## Breaking Changes

When breaking changes are identified during review (schema changes, API contract changes, etc.), they must be communicated clearly.

### During "Ready to PR"

Add a `### Breaking Changes` section to the PR body (between Summary and Details):

```markdown
## Summary
...

### Breaking Changes
- `TypeName.field` changed from `Type!` to `Type` — clients must handle nullable values
- Description of impact and what consumers need to update

## Details
...
```

Only include this section when there are actual breaking changes. Omit it otherwise.

### After PR Creation

If the PR contains breaking changes, **post a comment on the Linear task** summarizing them:

```
⚠️ Breaking Changes in PR #123:
- `TypeName.field` changed from `Type!` to `Type` — clients must handle nullable values
```

This ensures the team sees breaking changes even if they don't read the full PR description.

---

## Files Changed

A cumulative inventory of all files created, modified, or deleted. Updated incrementally as phases complete.

### Format

```markdown
## Files Changed

| File | Action | Phase |
|------|--------|-------|
| [`app/pos/models/foo.py`](../../app/pos/models/foo.py) | Added | 1 |
| [`app/pos/services/foo_service.py`](../../app/pos/services/foo_service.py) | Added | 2 |
| [`tests/pos/test_foo_service.py`](../../tests/pos/test_foo_service.py) | Added | 2 |
| [`app/pos/services/bar_service.py`](../../app/pos/services/bar_service.py) | Modified | 3 |
```

### Guidelines

- **Action**: `Added`, `Modified`, or `Deleted`
- **Phase**: Phase number, or `CDT` (Changes During Testing), `CPR` (Changes after PR Review)
- Use clickable relative links for file paths
- Update after each phase completion
- For hotfixes, use `Impl` instead of phase numbers

---

## Results Table

Add a Results section **from the beginning** of the document (at the end) with TBD values:

```markdown
## Results

| Metric | Value |
|--------|-------|
| Duration | TBD |
| Phases | N |
| Files Modified | TBD |
| Tests Added | TBD |
```

**IMPORTANT**: Keep TBD values throughout implementation and verification phases. Only fill in actual values when the user says **"Complete the plan/hotfix"** (after PR is merged). This is because additional changes may be needed during later phases (review, PR feedback, etc.).
