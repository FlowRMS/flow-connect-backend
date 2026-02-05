from datetime import datetime
from uuid import UUID

import strawberry

from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class SalesTeamMemberResponse:
    id: UUID
    user_id: UUID
    position: int
    user: UserResponse
    created_at: datetime
