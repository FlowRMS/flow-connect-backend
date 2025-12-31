from typing import TypeVar
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import (
    BaseModel,
    RbacPermission,
    RbacPrivilegeOptionEnum,
    RbacPrivilegeTypeEnum,
    RbacResourceEnum,
    RbacRoleEnum,
)
from sqlalchemy import Select, select

from app.graphql.v2.rbac.repositories.rbac_repository import RbacRepository
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy

T = TypeVar("T", bound=BaseModel)

PermissionCacheKey = tuple[int, int, int]


class RbacFilterService:
    def __init__(self, repository: RbacRepository, auth_info: AuthInfo) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_privilege_option(
        self,
        roles: list[RbacRoleEnum],
        resource: RbacResourceEnum,
        privilege: RbacPrivilegeTypeEnum = RbacPrivilegeTypeEnum.VIEW,
    ) -> RbacPrivilegeOptionEnum | None:
        """
        Get the highest privilege option for a user's roles on a resource.

        Returns ALL if any role has ALL access, OWN if any has OWN, None if no access.
        """
        stmt = (
            select(RbacPermission.option)
            .where(
                RbacPermission.role.in_(roles),
                RbacPermission.resource == resource,
                RbacPermission.privilege == privilege,
            )
            .order_by(RbacPermission.option.desc())
        )
        result = await self.repository.session.execute(stmt)
        options = result.scalars().all()

        if RbacPrivilegeOptionEnum.ALL in options:
            return RbacPrivilegeOptionEnum.ALL

        if RbacPrivilegeOptionEnum.OWN in options:
            return RbacPrivilegeOptionEnum.OWN

        return None

    async def get_permission_option(
        self,
        resource: RbacResourceEnum,
        privilege: RbacPrivilegeTypeEnum,
    ) -> RbacPrivilegeOptionEnum | None:
        """
        Get the permission option (ALL or OWN) for the current user's primary role.

        Uses auth_info.roles[0] as the primary role for permission lookup.
        Returns ALL if user has full access, OWN if restricted to owned entities,
        or None if no permission.
        """
        return await self.get_privilege_option(
            self.auth_info.roles,
            resource,
            privilege,
        )

    def requires_ownership_check(self, option: RbacPrivilegeOptionEnum | None) -> bool:
        return option == RbacPrivilegeOptionEnum.OWN

    async def apply_filter(
        self,
        stmt: Select,
        strategy: RbacFilterStrategy,
        user_id: UUID,
        roles: list[RbacRoleEnum],
        privilege: RbacPrivilegeTypeEnum = RbacPrivilegeTypeEnum.VIEW,
    ) -> Select:
        """
        Apply RBAC filtering to a query using the provided strategy.

        Args:
            stmt: The base select statement
            strategy: The filter strategy to use
            user_id: Current user's ID
            roles: User's role names
            privilege: The privilege type to check (default: VIEW)

        Returns:
            The filtered select statement (or empty result if no access)
        """
        option = await self.get_privilege_option(roles, strategy.resource, privilege)
        print(f"Option: {option.name if option else 'None'}")

        if option is None:
            return stmt

        return strategy.apply_filter(stmt, user_id, option)
