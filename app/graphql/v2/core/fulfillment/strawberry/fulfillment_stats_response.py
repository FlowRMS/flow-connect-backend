import strawberry


@strawberry.type
class FulfillmentStatsResponse:
    pending_count: int
    in_progress_count: int
    completed_count: int
    backorder_count: int
