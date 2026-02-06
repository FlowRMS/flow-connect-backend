from unittest.mock import MagicMock, patch

import pytest

from app.tenant_provisioning.migration_service import MigrationService


class TestMigrationService:
    @pytest.fixture
    def service(self) -> MigrationService:
        return MigrationService(
            alembic_config_path="alembic.ini",
        )

    @pytest.mark.asyncio
    async def test_get_current_revision_empty_db(
        self,
        service: MigrationService,
    ) -> None:
        """Returns None for uninitialized database."""
        mock_context = MagicMock()
        mock_context.get_current_revision.return_value = None

        with patch(
            "app.tenant_provisioning.migration_service.MigrationContext",
        ) as mock_ctx_class:
            mock_ctx_class.configure.return_value = mock_context

            with patch(
                "app.tenant_provisioning.migration_service.create_engine",
            ):
                result = await service.get_current_revision(
                    "postgresql://user:pass@localhost/test_db"
                )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_revision_migrated_db(
        self,
        service: MigrationService,
    ) -> None:
        """Returns version string for migrated database."""
        mock_context = MagicMock()
        mock_context.get_current_revision.return_value = "abc123def456"

        with patch(
            "app.tenant_provisioning.migration_service.MigrationContext",
        ) as mock_ctx_class:
            mock_ctx_class.configure.return_value = mock_context

            with patch(
                "app.tenant_provisioning.migration_service.create_engine",
            ):
                result = await service.get_current_revision(
                    "postgresql://user:pass@localhost/test_db"
                )

        assert result == "abc123def456"

    @pytest.mark.asyncio
    async def test_run_migrations_applies_all(
        self,
        service: MigrationService,
    ) -> None:
        """Migrations applied successfully returns new revision."""
        with patch(
            "app.tenant_provisioning.migration_service.command",
        ) as mock_command:
            with patch(
                "app.tenant_provisioning.migration_service.Config",
            ):
                with patch.object(
                    service,
                    "get_current_revision",
                    return_value="new_revision_123",
                ):
                    result = await service.run_migrations(
                        "postgresql://user:pass@localhost/test_db"
                    )

        mock_command.upgrade.assert_called_once()
        assert result == "new_revision_123"

    @pytest.mark.asyncio
    async def test_run_migrations_creates_schema(
        self,
        service: MigrationService,
    ) -> None:
        """Migration creates the version table schema if needed."""
        with patch(
            "app.tenant_provisioning.migration_service.command",
        ) as mock_command:
            with patch(
                "app.tenant_provisioning.migration_service.Config",
            ):
                with patch.object(
                    service,
                    "get_current_revision",
                    return_value="head_revision",
                ):
                    await service.run_migrations(
                        "postgresql://user:pass@localhost/test_db"
                    )

        # upgrade should be called with "head"
        call_args = mock_command.upgrade.call_args
        assert call_args[0][1] == "head"
