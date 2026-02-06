# Automated PR Plan Review Agent

- **Status**: 🟦 Complete
- **Linear Task**: [FLO-1622](https://linear.app/flow-labs/issue/FLO-1622/automated-pr-plan-review-agent)
- **Created**: 2026-02-05 22:46 -03
- **Approved**: 2026-02-05 22:59 -03
- **Finished**: 2026-02-06 08:55 -03
- **PR**: [#41](https://github.com/FlowRMS/flow-py-connect/pull/41)
- **Commit Prefix**: PR Review Agent

---

## Table of Contents

- [Overview](#overview)
- [Design Decisions](#design-decisions)
- [Phase 1: Review Script Core](#phase-1-review-script-core)
- [Phase 2: API Integrations](#phase-2-api-integrations)
- [Phase 3: GitHub Actions Workflow](#phase-3-github-actions-workflow)
- [Verification](#verification)
- [Review](#review)
- [Files Changed](#files-changed)
- [Results](#results)

---

## Overview

Create a GitHub Actions workflow that automatically reviews PRs containing plan or hotfix documents. When a PR is opened or updated, the agent:

1. **Detects** plan/hotfix documents in the changed files (`docs/plans/**/*.md` or `docs/hot-fixes/**/*.md`)
2. **Collects context**: plan document content, PR diff, commit log, Linear task description
3. **Sends structured prompt** to Claude API with the methodology standards and context
4. **Posts a PR comment** with a structured review table and recommendation
5. **Notifies via Linear** based on concern level:
   - **Pass/Warning**: Comment on Linear task, move to "Ready to merge to staging", mention PR reviewer (if assigned)
   - **Concern (red)**: Comment on Linear task mentioning the task assignee (main dev), move task back to "Todo", **block the PR** (required status check)

### Review Checks

| # | Check | What it verifies |
|---|-------|-----------------|
| 1 | Plan structure | 10-block order, required blocks present, correct status |
| 2 | Linear alignment | Plan overview matches task description |
| 3 | Plan concerns | Scope, complexity, missing edge cases, architectural issues |
| 4 | Files match plan | Modified files documented in Files Changed table |
| 5 | Commit policy | All commit points present, correct format, single-line |
| 6 | Code quality | File length, patterns, backend-standards.md compliance |

### Concern Levels

| Level | Icon | PR Status | Linear Action |
|-------|------|-----------|---------------|
| Pass | :green_circle: | Approve | Comment + move to "Ready to merge to staging" + mention reviewer |
| Warning | :yellow_circle: | Approve | Comment with warnings + move to "Ready to merge to staging" + mention reviewer |
| Concern | :red_circle: | **Block** | Comment mentioning task assignee + move task to "Todo" |

### Missing Linear Task = Red Flag

If the plan/hotfix document has no Linear task link, the review automatically flags this as a :red_circle: concern.

### Configuration

**Required GitHub Secrets:**
- `ANTHROPIC_API_KEY` - Claude API key
- `LINEAR_API_KEY` - Linear API key for posting comments and updating task status

**Required GitHub Settings:**
- Add `pr-plan-review` as a required status check to block merging on :red_circle: concerns

---

## Design Decisions

### DD-1: Custom Python script over Claude Code GitHub Action

**Decision**: Build a custom Python script that calls the Claude API directly, rather than using Anthropic's Claude Code GitHub Action.

- Full control over prompt structure, output format, and concern level logic
- Can integrate with Linear API (the GitHub Action doesn't support this natively)
- Can produce deterministic, structured output (JSON-based review) rather than free-form text
- Pattern: **Strategy Pattern** (Gang of Four) — each review check is an independent strategy that produces a structured result

### DD-2: Claude Sonnet for cost-effective reviews

**Decision**: Use `claude-sonnet-4-5-20250929` for the review API calls.

- Reviews run on every PR push, so cost matters
- Sonnet is capable enough for structured analysis against known rules
- Can upgrade to Opus for specific checks if needed

### DD-3: Modular script architecture

**Decision**: Split the review script into focused modules under `scripts/pr_review/`.

- `main.py` — Entry point, orchestration
- `collector.py` — Context collection (plan content, diff, commits, Linear task)
- `reviewer.py` — Claude API interaction, prompt building, response parsing
- `notifier.py` — GitHub PR comment posting + Linear comment/status updates
- `models.py` — Data models for review checks and results
- Each module stays under 300 lines (project standard)
- Pattern: **Pipes and Filters** (POSA) — collect → review → notify pipeline

### DD-4: Methodology docs embedded in prompt

**Decision**: Embed the key methodology rules directly in the Claude API prompt rather than uploading the full documents.

- The full docs are ~500+ lines each — too large for every API call
- Extract only the verifiable rules: block structure table, commit policy table, review checklist, file length limits
- Keeps token usage reasonable and focused
- Update the embedded rules when methodology docs change

---

## Phase 1: Review Script Core

_Data models, context collection, and the review orchestration pipeline._

### 1.1 RED: Write failing tests for models and collector ✅

**Test scenarios:**
- `test_review_check_model` — ReviewCheck with level, notes
- `test_review_result_aggregation` — Overall level is worst of individual checks
- `test_detect_plan_in_changed_files` — Finds plan/hotfix docs in file list
- `test_extract_linear_task_from_plan` — Parses `**Linear Task**: [FLO-1234](url)` from plan header
- `test_collect_context_builds_review_context` — Assembles plan content, diff, commits into ReviewContext

### 1.2 GREEN: Implement models and collector ✅

**Files:**
- `scripts/pr_review/__init__.py`
- `scripts/pr_review/models.py` — `ConcernLevel`, `ReviewCheck`, `ReviewResult`, `ReviewContext`
- `scripts/pr_review/collector.py` — `detect_plan_docs()`, `extract_linear_task_id()`, `collect_context()`

### 1.3 REFACTOR: Clean up and verify ✅
- `task all` passes (lint ✅, typecheck ✅, gql ✅)

---

## Phase 2: API Integrations

_Claude API reviewer, GitHub PR commenter, and Linear notifier._

### 2.1 RED: Write failing tests for reviewer and notifier ✅

**Test scenarios:**
- `test_build_review_prompt` — Prompt includes methodology rules and context
- `test_parse_claude_response` — Parses structured JSON response into ReviewResult
- `test_format_pr_comment` — Generates markdown table with checks and recommendation
- `test_determine_linear_action` — Correct action based on concern level (pass/warning/concern)
- `test_missing_linear_task_is_red` — No Linear task link → automatic red concern

### 2.2 GREEN: Implement reviewer and notifier ✅

**Files:**
- `scripts/pr_review/reviewer.py` — `build_prompt()`, `call_claude_api()`, `parse_response()`
- `scripts/pr_review/notifier.py` — `post_pr_comment()`, `post_linear_comment()`, `update_linear_status()`
- `scripts/pr_review/main.py` — Entry point: collect → review → notify

### 2.3 REFACTOR: Clean up and verify ✅
- `task all` passes (lint ✅, typecheck ✅, gql ✅)

---

## Phase 3: GitHub Actions Workflow

_The YAML workflow file and integration testing._

### 3.1 GREEN: Create GitHub Actions workflow ✅

**File:** `.github/workflows/pr-plan-review.yml`

**Workflow:**
```yaml
name: PR Plan Review
on:
  pull_request:
    types: [opened, synchronize, ready_for_review]

jobs:
  review:
    runs-on: ubuntu-latest
    # Only run if plan/hotfix docs are in the changed files
    steps:
      - Checkout code
      - Detect plan/hotfix documents in changed files
      - If no plan docs → skip (exit success)
      - Set up Python + install dependencies
      - Run scripts/pr_review/main.py
      - Post results (handled by the script via GitHub/Linear APIs)
```

### 3.2 GREEN: Create requirements file for CI ✅

**File:** `scripts/pr_review/requirements.txt` — `anthropic`, `httpx` (for Linear API calls)

### 3.3 REFACTOR: Clean up and verify ✅
- `task all` passes (lint ✅, typecheck ✅, gql ✅)

---

## Verification

### Step 1: Run tests
- `task test` — ✅ 41/41 passed (re-verified after review bug fixes)

### Step 2: Run task all
- `task all` — ✅ lint, typecheck, gql all pass (re-verified after review bug fixes)

### Step 3: Verify schema.graphql
- N/A — no GraphQL types modified

### Step 4: Manual testing

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Detect plan docs from actual git diff | Plan doc found in changed files list | ✅ Re-verified after review fixes |
| 2 | PR comment formatting | Markdown table with icons renders correctly | ✅ Re-verified after review fixes |
| 3 | Missing Linear task detection | Automatic red concern when no task link | ✅ Re-verified after review fixes |
| 4 | Concern level aggregation | Overall level matches worst individual check | ✅ Re-verified after review fixes |
| 5 | Skip when no plan docs | Returns empty list, no errors | ✅ Re-verified after review fixes |

---

## Review

| # | Check | Status |
|---|-------|--------|
| 1 | Performance impact | ✅ No concerns — standalone CI script, no app runtime impact |
| 2 | Effects on other features | ✅ No coupling to `app/` — isolated `scripts/` package |
| 3 | Code quality | ✅ All files under 300 lines, type hints, Python 3.13 syntax, enums, dataclasses |
| 4 | Potential bugs | ✅ Fixed — 3 bugs found and resolved during review (base_ref prefix, Linear issue UUID, Linear state UUID) |
| 5 | Commit policy | ✅ 5 commits, single-line, correct prefix and commit points |
| 6 | Breaking changes | ✅ None — all new files |
| 7 | Document updates | ✅ Verification and review sections updated |

## Files Changed

| File | Action | Phase |
|------|--------|-------|
| `scripts/__init__.py` | Added | P1 |
| `scripts/pr_review/__init__.py` | Added | P1 |
| `scripts/pr_review/models.py` | Added | P1 |
| `scripts/pr_review/collector.py` | Added | P1 |
| `tests/scripts/__init__.py` | Added | P1 |
| `tests/scripts/pr_review/__init__.py` | Added | P1 |
| `tests/scripts/pr_review/test_models.py` | Added | P1 |
| `tests/scripts/pr_review/test_collector.py` | Added | P1 |
| `scripts/pr_review/reviewer.py` | Added | P2 |
| `scripts/pr_review/notifier.py` | Added | P2 |
| `scripts/pr_review/main.py` | Added | P2 |
| `tests/scripts/pr_review/test_reviewer.py` | Added | P2 |
| `tests/scripts/pr_review/test_notifier.py` | Added | P2 |
| `.github/workflows/pr-plan-review.yml` | Added | P3 |
| `scripts/pr_review/requirements.txt` | Added | P3 |
| `scripts/pr_review/notifier.py` | Modified | Review |
| `scripts/pr_review/main.py` | Modified | Review |
| `tests/scripts/pr_review/test_notifier.py` | Modified | Review |

## Results

| Metric | Value |
|--------|-------|
| Duration | ~10 hours |
| Phases | 3 |
| Files Modified | 16 |
| Tests Added | 41 |
