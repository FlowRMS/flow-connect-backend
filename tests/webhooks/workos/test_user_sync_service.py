import uuid
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

import pytest
from commons.db.models.tenant import Tenant
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user import User

from app.webhooks.workos.services.user_sync_service import (
    WORKOS_ROLE_TO_RBAC,
    UserSyncService,
)


def create_mock_workos_user(
    user_id: str = "user_01ABC",
    email: str = "test@example.com",
    first_name: str = "Test",
    last_name: str = "User",
    external_id: str | None = None,
) -> MagicMock:
    user = MagicMock()
    user.id = user_id
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.external_id = external_id
    return user


def create_mock_membership(
    org_id: str = "org_01XYZ",
    role_slug: str = "inside_rep",
    membership_id: str = "mem_01ABC",
) -> MagicMock:
    membership = MagicMock()
    membership.id = membership_id
    membership.organization_id = org_id
    membership.role = {"slug": role_slug}
    return membership


def create_mock_event(workos_user: MagicMock) -> MagicMock:
    event = MagicMock()
    event.data = workos_user
    return event


def create_mock_tenant(
    tenant_id: uuid.UUID | None = None,
    org_id: str = "org_01XYZ",
    url: str = "test-tenant",
) -> Tenant:
    tenant = MagicMock(spec=Tenant)
    tenant.id = tenant_id or uuid.uuid4()
    tenant.org_id = org_id
    tenant.url = url
    return tenant


def create_mock_local_user(
    user_id: uuid.UUID | None = None,
    email: str = "test@example.com",
    role: RbacRoleEnum = RbacRoleEnum.INSIDE_REP,
    auth_provider_id: str | None = None,
) -> User:
    user = MagicMock(spec=User)
    user.id = user_id or uuid.uuid4()
    user.email = email
    user.role = role
    user.auth_provider_id = auth_provider_id
    return user


def create_mock_scoped_session(mock_session: AsyncMock) -> MagicMock:
    mock_begin = MagicMock()
    mock_begin.__aenter__ = AsyncMock(return_value=None)
    mock_begin.__aexit__ = AsyncMock(return_value=None)
    mock_session.begin = MagicMock(return_value=mock_begin)

    mock_scoped = MagicMock()
    mock_scoped.__aenter__ = AsyncMock(return_value=mock_session)
    mock_scoped.__aexit__ = AsyncMock(return_value=None)
    return mock_scoped


@dataclass
class MockDependencies:
    controller: MagicMock
    tenants_repo: AsyncMock
    workos_service: AsyncMock
    session: AsyncMock

    def create_service(self) -> UserSyncService:
        return UserSyncService(
            controller=self.controller,
            tenants_repository=self.tenants_repo,
            workos_service=self.workos_service,
        )

    def set_membership(self, membership: MagicMock) -> None:
        self.workos_service.client.user_management.list_organization_memberships = (
            AsyncMock(return_value=MagicMock(data=[membership]))
        )

    def set_no_membership(self) -> None:
        self.workos_service.client.user_management.list_organization_memberships = (
            AsyncMock(return_value=MagicMock(data=[]))
        )

    def set_tenant(self, tenant: Tenant | None) -> None:
        self.tenants_repo.get_by_org_id = AsyncMock(return_value=tenant)

    def set_local_user(self, local_user: User | None) -> None:
        self.session.execute = AsyncMock(
            return_value=MagicMock(
                scalar_one_or_none=MagicMock(return_value=local_user)
            )
        )

    async def run_user_created(
        self,
        event: MagicMock,
        membership: MagicMock,
        tenant: Tenant,
        local_user: User | None = None,
    ) -> UserSyncService:
        self.set_membership(membership)
        self.set_tenant(tenant)
        self.set_local_user(local_user)
        service = self.create_service()
        await service.handle_user_created(event)
        return service


@pytest.fixture
def mock_deps() -> MockDependencies:
    mock_session = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.add = MagicMock()

    mock_controller = MagicMock()
    mock_controller.scoped_session = MagicMock(
        return_value=create_mock_scoped_session(mock_session)
    )

    mock_tenants_repo = AsyncMock()
    mock_workos_service = AsyncMock()
    mock_workos_service.client.user_management.update_user = AsyncMock()
    mock_workos_service.client.user_management.update_organization_membership = (
        AsyncMock()
    )

    return MockDependencies(
        controller=mock_controller,
        tenants_repo=mock_tenants_repo,
        workos_service=mock_workos_service,
        session=mock_session,
    )


class TestUserSyncServiceSkipConditions:

    @pytest.mark.asyncio
    async def test_skip_if_external_id_exists(self) -> None:
        workos_user = create_mock_workos_user(external_id="existing_external_id")
        event = create_mock_event(workos_user)

        mock_controller = AsyncMock()
        mock_tenants_repo = AsyncMock()
        mock_workos_service = AsyncMock()

        service = UserSyncService(
            controller=mock_controller,
            tenants_repository=mock_tenants_repo,
            workos_service=mock_workos_service,
        )

        await service.handle_user_created(event)

        mock_tenants_repo.get_by_org_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_skip_if_no_organization(self, mock_deps: MockDependencies) -> None:
        workos_user = create_mock_workos_user(external_id=None)
        event = create_mock_event(workos_user)

        mock_deps.set_no_membership()
        service = mock_deps.create_service()

        await service.handle_user_created(event)

        mock_deps.tenants_repo.get_by_org_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_skip_if_tenant_not_found(self, mock_deps: MockDependencies) -> None:
        workos_user = create_mock_workos_user(external_id=None)
        event = create_mock_event(workos_user)
        membership = create_mock_membership(org_id="org_unknown")

        mock_deps.set_membership(membership)
        mock_deps.set_tenant(None)
        service = mock_deps.create_service()

        await service.handle_user_created(event)

        mock_deps.tenants_repo.get_by_org_id.assert_called_once_with("org_unknown")
        mock_deps.controller.scoped_session.assert_not_called()


class TestUserSyncServiceLinkExistingUser:

    @pytest.mark.asyncio
    async def test_link_existing_user_by_email(
        self, mock_deps: MockDependencies
    ) -> None:
        local_user_id = uuid.uuid4()
        workos_user = create_mock_workos_user(
            user_id="user_01ABC",
            email="existing@example.com",
            external_id=None,
        )
        event = create_mock_event(workos_user)
        membership = create_mock_membership(org_id="org_01XYZ", role_slug="inside_rep")
        tenant = create_mock_tenant(org_id="org_01XYZ")
        local_user = create_mock_local_user(
            user_id=local_user_id,
            email="existing@example.com",
            role=RbacRoleEnum.INSIDE_REP,
            auth_provider_id=None,
        )

        await mock_deps.run_user_created(event, membership, tenant, local_user)

        assert local_user.auth_provider_id == "user_01ABC"
        mock_deps.workos_service.client.user_management.update_user.assert_called_once()
        call_kwargs = (
            mock_deps.workos_service.client.user_management.update_user.call_args.kwargs
        )
        assert call_kwargs["external_id"] == str(local_user_id)

    @pytest.mark.asyncio
    async def test_sync_role_to_workos_if_mismatch(
        self, mock_deps: MockDependencies
    ) -> None:
        local_user_id = uuid.uuid4()
        workos_user = create_mock_workos_user(
            user_id="user_01ABC",
            email="existing@example.com",
            external_id=None,
        )
        event = create_mock_event(workos_user)
        membership = create_mock_membership(
            org_id="org_01XYZ",
            role_slug="outside_rep",
            membership_id="mem_01ABC",
        )
        tenant = create_mock_tenant(org_id="org_01XYZ")
        local_user = create_mock_local_user(
            user_id=local_user_id,
            email="existing@example.com",
            role=RbacRoleEnum.ADMINISTRATOR,
            auth_provider_id=None,
        )

        await mock_deps.run_user_created(event, membership, tenant, local_user)

        mock_deps.workos_service.client.user_management.update_organization_membership.assert_called_once_with(
            organization_membership_id="mem_01ABC",
            role_slug="administrator",
        )


class TestUserSyncServiceCreateNewUser:

    @pytest.mark.asyncio
    async def test_create_new_user_if_not_exists(
        self, mock_deps: MockDependencies
    ) -> None:
        workos_user = create_mock_workos_user(
            user_id="user_01ABC",
            email="newuser@example.com",
            first_name="New",
            last_name="User",
            external_id=None,
        )
        event = create_mock_event(workos_user)
        membership = create_mock_membership(org_id="org_01XYZ", role_slug="inside_rep")
        tenant = create_mock_tenant(org_id="org_01XYZ")

        await mock_deps.run_user_created(event, membership, tenant, local_user=None)

        mock_deps.session.add.assert_called_once()
        created_user: User = mock_deps.session.add.call_args[0][0]
        assert created_user.email == "newuser@example.com"
        assert created_user.username == "newuser@example.com"
        assert created_user.first_name == "New"
        assert created_user.last_name == "User"
        assert created_user.role == RbacRoleEnum.INSIDE_REP
        assert created_user.enabled is True
        assert created_user.auth_provider_id == "user_01ABC"

        mock_deps.workos_service.client.user_management.update_user.assert_called_once()
        call_kwargs = (
            mock_deps.workos_service.client.user_management.update_user.call_args.kwargs
        )
        assert call_kwargs["user_id"] == "user_01ABC"
        assert call_kwargs["external_id"] == str(created_user.id)

    @pytest.mark.asyncio
    async def test_create_new_user_maps_owner_role(
        self, mock_deps: MockDependencies
    ) -> None:
        workos_user = create_mock_workos_user(
            user_id="user_02DEF",
            email="owner@example.com",
            external_id=None,
        )
        event = create_mock_event(workos_user)
        membership = create_mock_membership(org_id="org_01XYZ", role_slug="owner")
        tenant = create_mock_tenant(org_id="org_01XYZ")

        await mock_deps.run_user_created(event, membership, tenant, local_user=None)

        created_user: User = mock_deps.session.add.call_args[0][0]
        assert created_user.role == RbacRoleEnum.OWNER

    @pytest.mark.asyncio
    async def test_create_new_user_defaults_unknown_role(
        self, mock_deps: MockDependencies
    ) -> None:
        workos_user = create_mock_workos_user(
            user_id="user_03GHI",
            email="unknown@example.com",
            external_id=None,
        )
        event = create_mock_event(workos_user)
        membership = create_mock_membership(
            org_id="org_01XYZ", role_slug="nonexistent_role"
        )
        tenant = create_mock_tenant(org_id="org_01XYZ")

        await mock_deps.run_user_created(event, membership, tenant, local_user=None)

        created_user: User = mock_deps.session.add.call_args[0][0]
        assert created_user.role == RbacRoleEnum.INSIDE_REP


class TestBuildNewUser:

    @pytest.mark.parametrize(
        ("workos_slug", "expected_role"),
        list(WORKOS_ROLE_TO_RBAC.items()),
    )
    def test_role_mapping(
        self, workos_slug: str, expected_role: RbacRoleEnum
    ) -> None:
        workos_user = create_mock_workos_user(email="map@test.com")
        membership = create_mock_membership(role_slug=workos_slug)

        user = UserSyncService._build_new_user(workos_user, membership)

        assert user.role == expected_role

    def test_fields_from_workos_user(self) -> None:
        workos_user = create_mock_workos_user(
            user_id="user_99",
            email="full@test.com",
            first_name="Jane",
            last_name="Doe",
        )
        membership = create_mock_membership(role_slug="administrator")

        user = UserSyncService._build_new_user(workos_user, membership)

        assert user.email == "full@test.com"
        assert user.username == "full@test.com"
        assert user.first_name == "Jane"
        assert user.last_name == "Doe"
        assert user.auth_provider_id == "user_99"
        assert user.enabled is True
        assert user.id is not None

    def test_handles_none_names(self) -> None:
        workos_user = create_mock_workos_user(first_name=None, last_name=None)
        membership = create_mock_membership(role_slug="inside_rep")

        user = UserSyncService._build_new_user(workos_user, membership)

        assert user.first_name == ""
        assert user.last_name == ""
