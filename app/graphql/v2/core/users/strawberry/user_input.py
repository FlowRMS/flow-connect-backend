import strawberry
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user import User

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class UserInput(BaseInputGQL[User]):
    username: str
    first_name: str
    last_name: str
    email: str
    role: RbacRoleEnum
    enabled: bool = True
    inside: bool | None = None
    outside: bool | None = None

    def to_orm_model(self) -> User:
        return User(
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            role=self.role,
            enabled=self.enabled,
            inside=self.inside,
            outside=self.outside,
        )
