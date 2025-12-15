from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.core.users.models.user import UserV2


@strawberry.input
class UserInput(BaseInputGQL[UserV2]):
    username: str
    first_name: str
    last_name: str
    email: str
    role_id: UUID
    auth_provider_id: str
    enabled: bool = True
    inside: bool | None = None
    outside: bool | None = None
    supervisor_id: UUID | None = None

    def to_orm_model(self) -> UserV2:
        return UserV2(
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            role_id=self.role_id,
            auth_provider_id=self.auth_provider_id,
            enabled=self.enabled,
            inside=self.inside,
            outside=self.outside,
            supervisor_id=self.supervisor_id,
        )
