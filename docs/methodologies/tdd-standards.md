# TDD Standards

This document defines the Test-Driven Development methodology used for all coding work (plans and hotfixes).

---

## Table of Contents

- [Augmented Coding](#augmented-coding)
- [Test-Driven Development](#test-driven-development)
- [Phase Structure](#phase-structure)
- [Documentation Format](#documentation-format)
- [AI Review Checklist](#ai-review-checklist)
- [Context Management](#context-management)

---

## Augmented Coding

We practice **Augmented Coding**, not Vibe Coding:

| | **Vibe Coding** | **Augmented Coding** |
|---|---|---|
| Focus | Output only | Code quality + output |
| Tests | Optional | Essential (TDD) |
| Review | Minimal | Every change |

**We practice Augmented Coding**: Care about code quality, tests, and maintainability.

**When Vibe Coding is OK**: Spikes, prototypes, and learning experiments only - never production code.

---

## Test-Driven Development

All coding work must follow the **Red-Green-Refactor** cycle:

1. **RED**: Write failing tests first for the logical unit
2. **GREEN**: Implement the minimum code to make tests pass
3. **REFACTOR**: Clean up the implementation without changing behavior (separate step/commit)

### Exceptions to RED Step

- **Database Models**: Pure schema mappings (SQLAlchemy models) don't need unit tests - they're validated by type checking and integration

### Test File Structure

- Mirror the app structure: `tests/graphql/organizations/test_*.py`
- Use pytest with `@pytest.mark.asyncio` for async tests
- Mock external dependencies (database sessions, external services)
- Avoid code duplication even in tests - use `@pytest.mark.parametrize` or helper methods

### Granularity: Per Logical Unit

- Group related functionality together (e.g., CRUD operations for an entity, a complete flow)
- Follow the layer structure: Repository → Service → GraphQL
- Complete one logical unit before moving to the next

### Separate Structural from Behavioral Changes

Based on Kent Beck's "Tidy First":

- **GREEN steps** contain behavioral changes (new functionality)
- **REFACTOR steps** contain structural changes only (cleanup, no behavior change)
- Each should be a separate step so the user can commit them independently

---

## Phase Structure

Work must be organized into **Phases**. Phases depend on the task but common examples include:

- **DB Schema**: Models, migrations
- **Backend Core**: Repositories, services
- **GraphQL Layer**: Types, queries, mutations
- **Validation & Verification**: Integration tests, `task all`

Each phase contains RED-GREEN-REFACTOR cycles for its logical units:

```markdown
## Phase 2: Member Repository & Service
- [ ] 2.1 RED: Write failing tests for member CRUD
- [ ] 2.2 GREEN: Implement repository and service to pass tests
- [ ] 2.3 REFACTOR: Clean up, ensure type safety
- [ ] 2.4 VERIFY: Run `task all`, confirm all checks pass
```

### Phase Verification

Run `task all` after each REFACTOR step.

### Final Verification Phase

Every plan MUST include a final Verification phase with manual testing. This phase:

1. **Focuses on manual testing** (e.g., GraphQL playground, curl commands)
2. **Does NOT duplicate automated checks** - `task all` is already covered in VERIFY steps
3. **Tests real scenarios** - success cases, error cases, edge cases

**What to include in manual testing:**
- Test the happy path (success case)
- Test error cases (validation errors, not found, unauthorized)
- Verify state changes (e.g., status changed from PENDING to SENT)
- Check schema introspection if new types/fields were added

**Documentation format** - Use a table to track test status:

```markdown
| # | Test | Expected | Status |
|---|------|----------|--------|
| 1 | Call mutation with no data | `SomeError` | ✅ |
| 2 | Call mutation with valid data | `{ success: true }` | ⏸️ |
```

Status markers:
- ✅ = Passed
- ⏸️ = Blocked/Pending (document the blocker below the table)
- ❌ = Failed (document the failure and fix before proceeding)

---

## Documentation Format

**Principle**: Documents describe WHAT to build and test, not HOW (implementation details).

Documents should be **concise and intention-focused**:
- **DO**: Describe behaviors, data structures, method signatures, and test scenarios
- **DON'T**: Include full code blocks (code becomes stale and bloats the document)

### For Implementation Steps

Describe:
- File to create/modify
- Data structures (fields, types)
- Method signatures and behavior
- Key logic in plain language

### For Test Steps

List test scenarios with names and descriptions:

```markdown
**Test scenarios** (if writing tests):
- `test_empty_list_returns_empty_dict` - Returns `{}` when no input provided
- `test_groups_by_org_id` - Groups results correctly by organization
- `test_limits_to_max` - Respects maximum limit while preserving total count
```

### Rationale

Based on [Specification by Example](https://agilealliance.org/resources/books/specification-by-example/):
- Tests themselves serve as executable documentation
- Descriptive test names ARE the specification
- Full code in documents becomes outdated quickly
- Implementation details are written just-in-time during execution

### Exception: Interface Specifications

GraphQL schema definitions are acceptable in **Design Decisions** sections when they:
- Define the contract/interface (types, queries, mutations)
- Clarify structure that prose might leave ambiguous
- Are short and focused (not full implementations)

These serve as **specifications**, not implementation code. The distinction:
- **Implementation code** (Python, business logic) → DON'T include
- **Interface specifications** (GraphQL schema, API contracts) → OK in Design Decisions

---

## AI Review Checklist

When reviewing AI-generated code, watch for these red flags (Kent Beck's Warning Signs):

- [ ] **No unnecessary loops or complexity**: AI may add control structures that aren't needed
- [ ] **No unrequested features**: Even reasonable next steps should await explicit direction
- [ ] **Tests not manipulated**: AI must never delete, disable, or modify tests to make them pass
- [ ] **No "cheating"**: Implementation should actually solve the problem, not work around tests

If any warning sign appears, STOP and redirect before continuing.

---

## Context Management

- Use `/clear` between major phases to prevent context pollution
- When starting a new session, re-read the document to restore context
- Keep documents updated so they serve as the source of truth

---

## Opportunistic Refactor

When encountering pre-existing issues (type errors, lint warnings, etc.) while working on a task, attempt to fix them if reasonable. First attempt is to do the refactor when we have the chance.
