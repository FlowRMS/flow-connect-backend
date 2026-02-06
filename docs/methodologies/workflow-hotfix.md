# Hotfix Workflow

This document defines the workflow for creating, executing, and completing hotfixes.

Hotfixes are lightweight documents for bug fixes and small corrections discovered after deployment. Use hotfixes instead of full plans when:
- The issue is a bug fix, not a new feature
- The solution is known (no exploration/phases needed)
- The change is small and focused

**CRITICAL: Hotfixes follow the SAME approval workflow as plans. Do NOT implement the solution until the user explicitly says "Approve the hotfix". The document describes what WILL be done, not what HAS been done.**

---

## Prerequisites

**CRITICAL**: Before starting any hotfix work, you MUST read:
- [`docs/methodologies/tdd-standards.md`](tdd-standards.md) - TDD methodology (Red-Green-Refactor cycle)
- [`docs/methodologies/backend-standards.md`](backend-standards.md) - Python/SQLAlchemy/GraphQL coding standards
- [`docs/methodologies/workflow-common.md`](workflow-common.md) - Git, execution, and review standards

Do NOT proceed with implementation without reading these standards first.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Hotfix Creation](#hotfix-creation)
- [Hotfix Document Standards](#hotfix-document-standards)
- [Hotfix Status Values](#hotfix-status-values)
- [Status Workflow (Key Phrases)](#status-workflow-key-phrases)
- [Git Conventions](#git-conventions)
- [Execution Rules](#execution-rules)

**Document block order**: See [Document Block Structure](workflow-common.md#document-block-structure) for the mandatory block order that all hotfix documents must follow.

---

## Hotfix Creation

Hotfixes can be created from a Linear task or from a prompt. See [Creation Flows](workflow-common.md#creation-flows) for the two supported flows and [Quick Document Creation](workflow-common.md#quick-document-creation-preserve-context) for the early-creation pattern.

---

## Hotfix Document Standards

### Location & Naming

- **All hotfixes must be created in `./docs/hot-fixes/YYYY-MM/`** (organized by month)
- **Naming convention**: `YYYY-MM-DD-NN-kebab-case-title.md` where `NN` is an incremental number
- **Folder structure**:
  ```
  docs/hot-fixes/
  ├── 2026-01/
  │   ├── 2026-01-30-01-improve-remote-api-error-handling.md
  │   └── ...
  ├── 2026-02/
  │   └── ...
  ```
- Create new month folders as needed

### Structure Requirements

- **Table of Contents** - Add a TOC after the header section with links to each block
- Hotfixes use Problem/Cause/Solution as the Overview block
- Hotfixes always have exactly 1 implementation phase + standalone Verification

### Hotfix Template

```markdown
# Hotfix: [Short Title]

- **Status**: 🔴 New
- **Related Plan**: [Link to original plan if applicable]
- **Linear Task**: [Link if separate task exists]
- **Created**: YYYY-MM-DD HH:MM TZ
- **Approved**: YYYY-MM-DD HH:MM TZ  <!-- Add when approved -->
- **Finished**: YYYY-MM-DD HH:MM TZ  <!-- Add when complete -->
- **PR**: [Link when ready]
- **Commit Prefix**: [Short prefix for commits]

---

## Table of Contents

- [Problem](#problem)
- [Cause](#cause)
- [Solution](#solution)
- [Phase 1: Implementation](#phase-1-implementation)
- [Verification](#verification)
- [Review](#review)
- [Files Changed](#files-changed)
- [Results](#results)

---

## Problem
[What's broken - include error messages, screenshots, or reproduction steps]

## Cause
[Root cause analysis - why it happened]

## Solution
[What needs to change to fix the issue - describe the changes, do NOT implement yet]

## Phase 1: Implementation

_TDD cycle: write tests, fix code, verify._

### 1.1 RED: Write failing tests
[Test scenarios that reproduce the bug]

### 1.2 GREEN: Implement fix
[Implementation details]

### 1.3 REFACTOR: Clean up and verify
- `task all` passes

## Verification

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Test scenario | Expected result | |

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | |
| 2 | Effects on other features | |
| 3 | Code quality ([backend-standards.md](../../docs/methodologies/backend-standards.md)) | |
| 4 | Potential bugs | |
| 5 | Commit policy | |
| 6 | Breaking changes | |
| 7 | Document updates | |

## Files Changed

| File | Action | Phase |
|------|--------|-------|

## Results

| Metric | Value |
|--------|-------|
| Duration | TBD |
| Files Modified | TBD |
| Tests Added | TBD |
```

See [Results Table](workflow-common.md#results-table) for guidance on when to fill values.

---

## Hotfix Status Values

Use these standardized statuses:

| Status | Description | Trigger |
|--------|-------------|---------|
| 🔴 New | Initial state when hotfix is first created | - |
| 🔵 Approved | Hotfix approved, ready for execution | **"Approve the hotfix"** |
| 🟡 In Progress - Implementation | TDD cycle: write tests, fix code, `task all` | **"Implement the hotfix"** |
| 🟡 In Progress - Verification | Manual testing against running server | **"Go to next phase"** |
| 🟢 Steps Done | All steps completed (implementation + verification) | Verification complete |
| 🔍 Reviewing | Pre-PR review in progress | **"Review changes"** |
| 🟤 PR Ready | PR created, awaiting merge | **"Ready to PR"** |
| 🟡 In Progress - PR Changes | Addressing human PR review feedback | **"Address PR review"** |
| 🟦 Complete | Hotfix fully complete | **"Complete the hotfix"** |

---

## Status Workflow (Key Phrases)

These status transitions require explicit user approval with the specified key phrases:

| From | To | Key Phrase | Actions |
|------|-----|------------|---------|
| 🔴 New | 🔵 Approved | **"Approve the hotfix"** | Add **Approved** date, create branch, commit document |
| 🔵 Approved | 🟡 In Progress - Implementation | **"Implement the hotfix"** | Begin TDD cycle |
| 🟡 In Progress - Implementation | 🟡 In Progress - Verification | **"Go to next phase"** | Commit implementation, begin manual testing |
| 🟡 In Progress - Verification | 🟢 Steps Done | (automatic) | When verification is complete |
| 🟢 Steps Done | 🔍 Reviewing | **"Review changes"** | Commit uncommitted changes, perform review |
| 🔍 Reviewing | 🟤 PR Ready | **"Ready to PR"** | Push changes, create PR, add **PR** link |
| 🟤 PR Ready | 🟡 In Progress - PR Changes | **"Address PR review"** | Begin PR feedback changes |
| 🟡 In Progress - PR Changes | 🟤 PR Ready | (automatic) | Changes done, re-verify, re-review, push |
| 🟤 PR Ready | 🟦 Complete | **"Complete the hotfix"** | Add **Finished** date, fill Results table, commit, push |

**IMPORTANT**: Wait for explicit key phrases before changing status. Do NOT implement until user says "Approve the hotfix".

**⚠️ PR REVIEW CYCLE**: After "Ready to PR", the reviewer may request changes. Use **"Address PR review"** to handle this — it triggers an automatic cycle of changes → re-verification → re-review → push.

### When user says "Approve the hotfix"

1. Update status to 🔵 Approved and add **Approved** date
2. Create hotfix branch from main: `git checkout main && git pull && git checkout -b hotfix/[name]`
3. Make initial commit with the hotfix document
4. Wait for user to say **"Implement the hotfix"** before beginning implementation

### When user says "Implement the hotfix"

1. Update status to 🟡 In Progress - Implementation
2. Begin implementing the fix following TDD standards:
   - **RED**: Write a failing test that reproduces the bug
   - **GREEN**: Fix the code to make the test pass
   - **REFACTOR**: Clean up if needed
3. Run `task all` to verify all checks pass
4. Update the [Files Changed](workflow-common.md#files-changed) table (use `Impl` as the Phase value)
5. **STOP** and wait for user to say **"Go to next phase"**

### When user says "Go to next phase"

1. Commit the implementation changes
2. Update status to 🟡 In Progress - Verification
3. Perform manual testing using the [Verification](workflow-common.md#verification) block
4. Update the manual testing table with results
5. When verification is complete:
   - Commit: `[Prefix] - Verification complete`
   - Update status to 🟢 Steps Done
6. **STOP** and wait for user to say **"Review changes"**

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
Title: Hotfix: [Same title as the hotfix document]

Body:
# Summary

[Brief overview of what the hotfix fixes]

**Task**: [Linear task title](Linear task link) (if applicable)
**Related Plan**: [Plan title](Plan link) (if applicable)

## Problem

[Brief description of the problem]

## Solution

[Brief description of the fix]

### Breaking Changes          <!-- only when applicable, omit otherwise -->
- Description of breaking change and impact

## Details

### Documents
1. **A** **`docs/hot-fixes/YYYY-MM-DD-NN-hotfix-name.md`** - Hotfix document

### GraphQL Schema
1. **M** `schema.graphql` - Description of schema changes

### App Changes
1. **M** `app/path/to/modified_file.py` - Description

### Tests
1. **A** `tests/path/to/test_file.py` - Description (if applicable)
```

4. **Link PR to Linear task** - See [PR to Linear Linking](workflow-common.md#pr-to-linear-linking)
5. Add the **PR** link to the hotfix header (do NOT commit yet - wait for "Complete the hotfix")
6. **Provide the GitHub PR link to the user** (e.g., "PR created: https://github.com/...")
7. **IMPORTANT**: Tell the user: `Say "Complete the hotfix" to finalize the hotfix document. After that, merge the PR.`

**⚠️ CRITICAL**: The next step is "Complete the hotfix", NOT merging the PR. The hotfix must be finalized BEFORE merging so the completed document is included in the merge.

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

### When user says "Complete the hotfix"

**IMPORTANT**: Complete the hotfix BEFORE merging the PR, so the finalized document is included in the merge.

1. Update status to 🟦 Complete and add **Finished** date
2. Fill in the Results table with actual values (Duration, Files Modified, Tests Added)
3. Commit and push the final hotfix document changes (status, PR link, Finished date, Results)

---

## Git Conventions

See [Git Workflow Standards](workflow-common.md#git-workflow-standards) for commit process details and examples.

### Hotfix-Specific Conventions

- **Branch naming**: `hotfix/[short-name]`
- **PR base branch**: `main`

### Commit Message Format

See [Commit Policy](workflow-common.md#commit-policy) for the full list of commit points.

| # | Commit Point | Message Format |
|---|-------------|----------------|
| 1 | Approved | `[Prefix] - Add hotfix document` |
| 2 | Implementation | `[Prefix] - Implementation - [Brief description]` |
| 3 | Verification | `[Prefix] - Verification complete` |
| 4 | CDT entry | `[Prefix] - CDT BF-1 - [Brief description]` |
| 5 | Review | `[Prefix] - Review complete` |
| 6 | CPR entry | `[Prefix] - PR review CH-1 - [Brief description]` |
| 7 | CPR re-verification | `[Prefix] - PR review - Verification complete` |
| 8 | CPR re-review | `[Prefix] - PR review - Review complete` |
| 9 | Complete | `[Prefix] - Complete` |

---

## Execution Rules

See [Execution Rules](workflow-common.md#execution-rules) for common standards.

### After Creating a Hotfix

- Say "The hotfix is ready for review" and provide the path to the document
- Wait for the user to explicitly say **"Approve the hotfix"**
- Never assume approval from other phrases or implicit signals

### Document Updates During Implementation

- Update the [Files Changed](workflow-common.md#files-changed) table as files are created/modified/deleted
- Update the **Status** field at the top when transitioning between states
