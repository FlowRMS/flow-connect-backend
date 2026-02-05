## PR #199 Fix Instructions

**IMPORTANT:** This file is for your use only and must be added to your `.gitignore` in your local branch.

---

### Files to fix:

#### 1. `app/workers/document_execution/converters/statement_converter.py`

The file is currently 318 lines, exceeding the 300-line limit. Split it into two files:

**Option A - Extract caching methods:**
- Create `app/workers/document_execution/converters/statement_converter_cache.py`
- Move these methods:
  - `_get_order` (lines 280-286)
  - `_find_invoice_by_number_and_factory` (lines 288-308)
  - `_order_cache` and `_invoice_cache` initialization
- Import and use the cache class in `StatementConverter`

**Option B - Extract resolution helpers:**
- Create `app/workers/document_execution/converters/statement_resolution_helpers.py`
- Move these methods:
  - `_resolve_order_id`
  - `_resolve_invoice_id`
  - `_match_order_detail`
  - `_get_order_detail`
- These can be standalone async functions that take the repository/session as a parameter

---

#### 2. `app/graphql/pre_opportunities/services/pre_opportunities_service.py`

Remove all redundant docstrings. The type hints make them unnecessary:

**Remove these docstrings:**
```python
# Line 25 - Remove class docstring
"""Service for PreOpportunity entity business logic."""

# Lines 41-52 - Remove method docstring for create_pre_opportunity
"""
Create a new pre-opportunity with balance calculation.
...
"""

# Lines 77-85 - Remove method docstring for update_pre_opportunity
"""
Update a pre-opportunity and recalculate balance.
...
"""

# Line 99 - Remove
"""Get a pre-opportunity by ID."""

# Line 124 - Remove
"""Delete a pre-opportunity by ID."""

# Line 129 - Remove
"""Get all pre-opportunities for a specific job."""

# Line 133 - Remove
"""Get all pre-opportunities for a specific customer."""

# Lines 140-149 - Remove search_pre_opportunities docstring
"""
Search pre-opportunities by entity number.
...
"""

# Lines 152-165 - Remove find_by_entity docstring
"""
Find all pre-opportunities linked to a specific entity.
...
"""
```

---

#### 3. `app/workers/document_execution/batch_processor.py` (Optional)

Consider removing or significantly shortening the class docstring on lines 33-39:

```python
class DocumentBatchProcessor:
    """
    Handles bulk document processing with error tracking and batch chunking.

    Processes DTOs in configurable batches, tracking which records were
    created, skipped, or failed. Coordinates with converters to handle
    deduplication and entity creation.
    """
```

The class name `DocumentBatchProcessor` combined with method names like `execute_bulk` and `_process_batch` make the purpose clear.

---

### Rules to follow:

1. **Max 300 lines per file** (excluding imports and blank lines)
2. **No redundant docstrings** that just restate function signatures
3. **Function names + type hints should be self-documenting**
4. **Every parameter must have a type hint** — no `Any` unless absolutely necessary
5. **Run `task all` before pushing** to ensure:
   - Type checks pass (basedpyright)
   - Linting passes (ruff)
   - All tests pass (pytest)

---

### Add this file to .gitignore:

Add the following line to your local `.gitignore`:

```
pr_199_claude_instructions.md
```
