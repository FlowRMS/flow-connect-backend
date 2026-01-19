import strawberry


@strawberry.type
class InventoryImportSummary:
    processed: int
    created: int
    updated: int
    errors: int
    skipped: int
