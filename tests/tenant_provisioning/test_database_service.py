from unittest.mock import AsyncMock, patch

import pytest

from app.tenant_provisioning.database_service import DatabaseCreationService


class TestDatabaseCreationService:
    @pytest.fixture
    def service(self) -> DatabaseCreationService:
        return DatabaseCreationService(
            pg_url="postgresql://user:pass@localhost:5432/postgres",
        )

    @pytest.mark.asyncio
    async def test_database_exists_returns_true(
        self,
        service: DatabaseCreationService,
    ) -> None:
        """Detects existing database."""
        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = True

        with patch.object(service, "_get_connection", return_value=mock_conn):
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            result = await service.database_exists("existing_db")

        assert result is True
        mock_conn.fetchval.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_not_exists_returns_false(
        self,
        service: DatabaseCreationService,
    ) -> None:
        """Detects missing database."""
        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = False

        with patch.object(service, "_get_connection", return_value=mock_conn):
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            result = await service.database_exists("nonexistent_db")

        assert result is False

    @pytest.mark.asyncio
    async def test_create_database_success(
        self,
        service: DatabaseCreationService,
    ) -> None:
        """Creates new PostgreSQL database."""
        mock_conn = AsyncMock()

        with patch.object(service, "_get_connection", return_value=mock_conn):
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            await service.create_database("new_tenant_db")

        mock_conn.execute.assert_called_once()
        call_args = mock_conn.execute.call_args[0][0]
        assert "CREATE DATABASE" in call_args
        assert "new_tenant_db" in call_args

    @pytest.mark.asyncio
    async def test_create_database_sanitizes_name(
        self,
        service: DatabaseCreationService,
    ) -> None:
        """Database name is properly quoted to prevent SQL injection."""
        mock_conn = AsyncMock()

        with patch.object(service, "_get_connection", return_value=mock_conn):
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            await service.create_database("tenant-with-hyphen")

        call_args = mock_conn.execute.call_args[0][0]
        # Should use quoted identifier
        assert '"tenant-with-hyphen"' in call_args
