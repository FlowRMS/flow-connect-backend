from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.db.db_provider import create_session, create_transient_session
from app.errors.common_errors import TenantNotFoundError


@pytest.fixture
def mock_auth_info() -> MagicMock:
    auth_info = MagicMock()
    auth_info.tenant_name = "test_tenant"
    return auth_info


@pytest.fixture
def mock_controller() -> MagicMock:
    return MagicMock()


class TestCreateSession:
    @pytest.mark.asyncio
    async def test_raises_tenant_not_found_error(
        self,
        mock_controller: MagicMock,
        mock_auth_info: MagicMock,
    ) -> None:
        mock_controller.scoped_session.return_value.__aenter__ = AsyncMock(
            side_effect=Exception("Tenant test_tenant not found"),
        )
        mock_controller.scoped_session.return_value.__aexit__ = AsyncMock()

        with pytest.raises(TenantNotFoundError, match="Tenant test_tenant not found"):
            async with create_session(mock_controller, mock_auth_info):  # type: ignore[arg-type]
                pass

    @pytest.mark.asyncio
    async def test_does_not_catch_other_exceptions(
        self,
        mock_controller: MagicMock,
        mock_auth_info: MagicMock,
    ) -> None:
        mock_controller.scoped_session.return_value.__aenter__ = AsyncMock(
            side_effect=RuntimeError("Connection refused"),
        )
        mock_controller.scoped_session.return_value.__aexit__ = AsyncMock()

        with pytest.raises(RuntimeError, match="Connection refused"):
            async with create_session(mock_controller, mock_auth_info):  # type: ignore[arg-type]
                pass


class TestCreateTransientSession:
    @pytest.mark.asyncio
    async def test_raises_tenant_not_found_error(
        self,
        mock_controller: MagicMock,
        mock_auth_info: MagicMock,
    ) -> None:
        mock_controller.transient_session.return_value.__aenter__ = AsyncMock(
            side_effect=Exception("Tenant test_tenant not found"),
        )
        mock_controller.transient_session.return_value.__aexit__ = AsyncMock()

        with pytest.raises(TenantNotFoundError, match="Tenant test_tenant not found"):
            async with create_transient_session(mock_controller, mock_auth_info):  # type: ignore[arg-type]
                pass

    @pytest.mark.asyncio
    async def test_does_not_catch_other_exceptions(
        self,
        mock_controller: MagicMock,
        mock_auth_info: MagicMock,
    ) -> None:
        mock_controller.transient_session.return_value.__aenter__ = AsyncMock(
            side_effect=RuntimeError("Connection refused"),
        )
        mock_controller.transient_session.return_value.__aexit__ = AsyncMock()

        with pytest.raises(RuntimeError, match="Connection refused"):
            async with create_transient_session(mock_controller, mock_auth_info):  # type: ignore[arg-type]
                pass
