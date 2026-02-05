import strawberry

from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class MismatchCheckResponse:
    has_mismatch: bool
    only_in_team: list[UserResponse]
    only_in_territory: list[UserResponse]
