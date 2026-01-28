"""Tests for warehouse repository and service soft-delete behavior."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.graphql.v2.core.warehouses.repositories.warehouse_repository import (
    WarehouseRepository,
)
from app.graphql.v2.core.warehouses.services.warehouse_service import WarehouseService


class TestWarehouseRepository:
    """Tests for WarehouseRepository soft-delete methods."""

    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_context_wrapper(self) -> MagicMock:
        context_wrapper = MagicMock()
        mock_context = MagicMock()
        mock_context.auth_info = MagicMock()
        mock_context.auth_info.flow_user_id = uuid4()
        mock_context.auth_info.roles = []
        context_wrapper.get.return_value = mock_context
        return context_wrapper

    @pytest.fixture
    def repository(
        self,
        mock_context_wrapper: MagicMock,
        mock_session: AsyncMock,
    ) -> WarehouseRepository:
        return WarehouseRepository(
            context_wrapper=mock_context_wrapper,
            session=mock_session,
        )

    async def test_soft_delete_sets_is_active_false(
        self,
        repository: WarehouseRepository,
        mock_session: AsyncMock,
    ) -> None:
        warehouse_id = uuid4()
        mock_warehouse = MagicMock()
        mock_warehouse.is_active = True

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_warehouse
        mock_session.execute.return_value = mock_result

        result = await repository.soft_delete(warehouse_id)

        assert result is mock_warehouse
        assert result.is_active is False
        mock_session.flush.assert_awaited_once()

    async def test_list_all_with_relations_excludes_soft_deleted(
        self,
        repository: WarehouseRepository,
        mock_session: AsyncMock,
    ) -> None:
        active_warehouse = MagicMock()

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [active_warehouse]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        result = await repository.list_all_with_relations()

        assert result == [active_warehouse]
        mock_session.execute.assert_awaited_once()

    async def test_get_with_relations_excludes_soft_deleted(
        self,
        repository: WarehouseRepository,
        mock_session: AsyncMock,
    ) -> None:
        warehouse_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_with_relations(warehouse_id)

        assert result is None
        mock_session.execute.assert_awaited_once()


class TestWarehouseService:
    """Tests for WarehouseService delete method."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        return AsyncMock(spec=WarehouseRepository)

    @pytest.fixture
    def service(self, mock_repository: AsyncMock) -> WarehouseService:
        return WarehouseService(
            repository=mock_repository,
            members_repository=AsyncMock(),
            settings_repository=AsyncMock(),
            structure_repository=AsyncMock(),
            auth_info=MagicMock(),
        )

    async def test_delete_calls_soft_delete_and_returns_true(
        self,
        service: WarehouseService,
        mock_repository: AsyncMock,
    ) -> None:
        warehouse_id = uuid4()
        mock_repository.soft_delete.return_value = MagicMock()

        result = await service.delete(warehouse_id)

        assert result is True
        mock_repository.soft_delete.assert_awaited_once_with(warehouse_id)
