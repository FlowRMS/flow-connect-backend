from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError


class TestSalesTeamsModuleImports:
    """Tests for sales teams module imports."""

    def test_sales_team_repository_import(self) -> None:
        """Test SalesTeamRepository can be imported."""
        from app.graphql.v2.core.sales_teams.repositories.sales_team_repository import (
            SalesTeamRepository,
        )

        assert SalesTeamRepository is not None

    def test_sales_team_member_repository_import(self) -> None:
        """Test SalesTeamMemberRepository can be imported."""
        from app.graphql.v2.core.sales_teams.repositories.sales_team_member_repository import (
            SalesTeamMemberRepository,
        )

        assert SalesTeamMemberRepository is not None

    def test_sales_team_service_import(self) -> None:
        """Test SalesTeamService can be imported."""
        from app.graphql.v2.core.sales_teams.services.sales_team_service import (
            SalesTeamService,
        )

        assert SalesTeamService is not None

    def test_sales_team_sync_service_import(self) -> None:
        """Test SalesTeamSyncService can be imported."""
        from app.graphql.v2.core.sales_teams.services.sales_team_sync_service import (
            SalesTeamSyncService,
        )

        assert SalesTeamSyncService is not None

    def test_sales_team_filter_strategy_import(self) -> None:
        """Test SalesTeamFilterStrategy can be imported."""
        from app.graphql.v2.rbac.strategies.sales_team_filter import (
            SalesTeamFilterStrategy,
        )

        assert SalesTeamFilterStrategy is not None

    def test_sales_team_queries_import(self) -> None:
        """Test SalesTeamQueries can be imported."""
        from app.graphql.v2.core.sales_teams.queries.sales_team_queries import (
            SalesTeamQueries,
        )

        assert SalesTeamQueries is not None

    def test_sales_team_mutations_import(self) -> None:
        """Test SalesTeamMutations can be imported."""
        from app.graphql.v2.core.sales_teams.mutations.sales_team_mutations import (
            SalesTeamMutations,
        )

        assert SalesTeamMutations is not None

    def test_sales_team_input_import(self) -> None:
        """Test SalesTeamInput can be imported."""
        from app.graphql.v2.core.sales_teams.strawberry.sales_team_input import (
            SalesTeamInput,
        )

        assert SalesTeamInput is not None

    def test_sales_team_response_import(self) -> None:
        """Test SalesTeamResponse can be imported."""
        from app.graphql.v2.core.sales_teams.strawberry.sales_team_response import (
            SalesTeamResponse,
        )

        assert SalesTeamResponse is not None


class TestSalesTeamService:
    """Tests for SalesTeamService business logic."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock SalesTeamRepository."""
        from app.graphql.v2.core.sales_teams.repositories.sales_team_repository import (
            SalesTeamRepository,
        )

        repo = AsyncMock(spec=SalesTeamRepository)
        return repo

    @pytest.fixture
    def mock_member_repository(self) -> AsyncMock:
        """Create a mock SalesTeamMemberRepository."""
        from app.graphql.v2.core.sales_teams.repositories.sales_team_member_repository import (
            SalesTeamMemberRepository,
        )

        repo = AsyncMock(spec=SalesTeamMemberRepository)
        return repo

    @pytest.fixture
    def service(
        self,
        mock_repository: AsyncMock,
        mock_member_repository: AsyncMock,
    ) -> "SalesTeamService":
        """Create a SalesTeamService with mocked dependencies."""
        from app.graphql.v2.core.sales_teams.services.sales_team_service import (
            SalesTeamService,
        )

        return SalesTeamService(
            repository=mock_repository,
            member_repository=mock_member_repository,
        )

    @pytest.mark.asyncio
    async def test_get_by_id_returns_team(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
    ) -> None:
        """Test get_by_id returns the sales team."""
        team_id = uuid4()
        mock_team = MagicMock()
        mock_team.id = team_id
        mock_repository.get_by_id.return_value = mock_team

        result = await service.get_by_id(team_id)

        assert result == mock_team
        mock_repository.get_by_id.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_raises_not_found_for_missing_team(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
    ) -> None:
        """Test get_by_id raises NotFoundError for missing team."""
        team_id = uuid4()
        mock_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Sales team"):
            await service.get_by_id(team_id)

    @pytest.mark.asyncio
    async def test_get_by_id_optional_returns_none_for_missing_team(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
    ) -> None:
        """Test get_by_id_optional returns None for missing team."""
        team_id = uuid4()
        mock_repository.get_by_id.return_value = None

        result = await service.get_by_id_optional(team_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_raises_error_for_duplicate_name(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
    ) -> None:
        """Test create raises NameAlreadyExistsError for duplicate name."""
        from app.graphql.v2.core.sales_teams.strawberry.sales_team_input import (
            SalesTeamInput,
        )

        mock_repository.name_exists.return_value = True

        input_data = SalesTeamInput(
            name="Existing Team",
            manager_id=uuid4(),
        )

        with pytest.raises(NameAlreadyExistsError, match="already exists"):
            await service.create(input_data)

        mock_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_success(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
    ) -> None:
        """Test create successfully creates a team."""
        from app.graphql.v2.core.sales_teams.strawberry.sales_team_input import (
            SalesTeamInput,
        )

        team_id = uuid4()
        mock_team = MagicMock()
        mock_team.id = team_id

        mock_repository.name_exists.return_value = False
        mock_repository.create.return_value = mock_team
        mock_repository.get_by_id.return_value = mock_team

        input_data = SalesTeamInput(
            name="New Team",
            manager_id=uuid4(),
        )

        result = await service.create(input_data)

        assert result == mock_team
        mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_raises_not_found_for_missing_team(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
    ) -> None:
        """Test delete raises NotFoundError for missing team."""
        team_id = uuid4()
        mock_repository.exists.return_value = False

        with pytest.raises(NotFoundError, match="Sales team"):
            await service.delete(team_id)

        mock_repository.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_success(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
    ) -> None:
        """Test delete successfully deletes team."""
        team_id = uuid4()
        mock_repository.exists.return_value = True
        mock_repository.delete.return_value = True

        result = await service.delete(team_id)

        assert result is True
        mock_repository.delete.assert_called_once_with(team_id)

    @pytest.mark.asyncio
    async def test_add_member_raises_not_found_for_missing_team(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
    ) -> None:
        """Test add_member raises NotFoundError for missing team."""
        team_id = uuid4()
        user_id = uuid4()
        mock_repository.exists.return_value = False

        with pytest.raises(NotFoundError, match="Sales team"):
            await service.add_member(team_id, user_id)

    @pytest.mark.asyncio
    async def test_add_member_skips_if_already_member(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
        mock_member_repository: AsyncMock,
    ) -> None:
        """Test add_member skips creation if user is already a member."""
        team_id = uuid4()
        user_id = uuid4()
        mock_team = MagicMock()
        mock_team.id = team_id

        mock_repository.exists.return_value = True
        mock_member_repository.get_by_sales_team_and_user.return_value = MagicMock()
        mock_repository.get_by_id.return_value = mock_team

        _ = await service.add_member(team_id, user_id)

        mock_member_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_member_creates_new_member(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
        mock_member_repository: AsyncMock,
    ) -> None:
        """Test add_member creates a new member if not exists."""
        team_id = uuid4()
        user_id = uuid4()
        mock_team = MagicMock()
        mock_team.id = team_id

        mock_repository.exists.return_value = True
        mock_member_repository.get_by_sales_team_and_user.return_value = None
        mock_repository.get_by_id.return_value = mock_team

        _ = await service.add_member(team_id, user_id)

        mock_member_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_member_raises_not_found_for_missing_member(
        self,
        service: "SalesTeamService",
        mock_member_repository: AsyncMock,
    ) -> None:
        """Test remove_member raises NotFoundError for missing member."""
        team_id = uuid4()
        user_id = uuid4()
        mock_member_repository.get_by_sales_team_and_user.return_value = None

        with pytest.raises(NotFoundError, match="Team member"):
            await service.remove_member(team_id, user_id)

    @pytest.mark.asyncio
    async def test_remove_member_success(
        self,
        service: "SalesTeamService",
        mock_repository: AsyncMock,
        mock_member_repository: AsyncMock,
    ) -> None:
        """Test remove_member successfully removes member."""
        team_id = uuid4()
        user_id = uuid4()
        member_id = uuid4()
        mock_member = MagicMock()
        mock_member.id = member_id
        mock_team = MagicMock()
        mock_team.id = team_id

        mock_member_repository.get_by_sales_team_and_user.return_value = mock_member
        mock_member_repository.delete.return_value = True
        mock_repository.get_by_id.return_value = mock_team

        result = await service.remove_member(team_id, user_id)

        assert result == mock_team
        mock_member_repository.delete.assert_called_once_with(member_id)


class TestSalesTeamSyncService:
    """Tests for SalesTeamSyncService business logic."""

    @pytest.fixture
    def mock_sales_team_repository(self) -> AsyncMock:
        """Create a mock SalesTeamRepository."""
        return AsyncMock()

    @pytest.fixture
    def mock_member_repository(self) -> AsyncMock:
        """Create a mock SalesTeamMemberRepository."""
        return AsyncMock()

    @pytest.fixture
    def mock_split_rate_repository(self) -> AsyncMock:
        """Create a mock TerritorySplitRateRepository."""
        return AsyncMock()

    @pytest.fixture
    def sync_service(
        self,
        mock_sales_team_repository: AsyncMock,
        mock_member_repository: AsyncMock,
        mock_split_rate_repository: AsyncMock,
    ) -> "SalesTeamSyncService":
        """Create a SalesTeamSyncService with mocked dependencies."""
        from app.graphql.v2.core.sales_teams.services.sales_team_sync_service import (
            SalesTeamSyncService,
        )

        return SalesTeamSyncService(
            sales_team_repository=mock_sales_team_repository,
            member_repository=mock_member_repository,
            split_rate_repository=mock_split_rate_repository,
        )

    @pytest.mark.asyncio
    async def test_check_list_mismatch_returns_no_mismatch_when_lists_match(
        self,
        sync_service: "SalesTeamSyncService",
        mock_member_repository: AsyncMock,
        mock_split_rate_repository: AsyncMock,
    ) -> None:
        """Test check_list_mismatch returns no mismatch when lists match."""
        team_id = uuid4()
        territory_id = uuid4()
        user1 = uuid4()
        user2 = uuid4()

        mock_member_repository.get_member_user_ids.return_value = [user1, user2]

        mock_rate1 = MagicMock()
        mock_rate1.user_id = user1
        mock_rate2 = MagicMock()
        mock_rate2.user_id = user2
        mock_split_rate_repository.get_by_territory.return_value = [
            mock_rate1,
            mock_rate2,
        ]

        has_mismatch, only_in_team, only_in_territory = (
            await sync_service.check_list_mismatch(team_id, territory_id)
        )

        assert has_mismatch is False
        assert only_in_team == []
        assert only_in_territory == []

    @pytest.mark.asyncio
    async def test_check_list_mismatch_detects_differences(
        self,
        sync_service: "SalesTeamSyncService",
        mock_member_repository: AsyncMock,
        mock_split_rate_repository: AsyncMock,
    ) -> None:
        """Test check_list_mismatch detects differences between lists."""
        team_id = uuid4()
        territory_id = uuid4()
        user1 = uuid4()
        user2 = uuid4()
        user3 = uuid4()

        mock_member_repository.get_member_user_ids.return_value = [user1, user2]

        mock_rate = MagicMock()
        mock_rate.user_id = user3
        mock_split_rate_repository.get_by_territory.return_value = [mock_rate]

        has_mismatch, only_in_team, only_in_territory = (
            await sync_service.check_list_mismatch(team_id, territory_id)
        )

        assert has_mismatch is True
        assert set(only_in_team) == {user1, user2}
        assert only_in_territory == [user3]

    @pytest.mark.asyncio
    async def test_sync_team_to_territory_replaces_territory_split_rates(
        self,
        sync_service: "SalesTeamSyncService",
        mock_member_repository: AsyncMock,
        mock_split_rate_repository: AsyncMock,
    ) -> None:
        """Test sync_team_to_territory replaces territory split rates."""
        team_id = uuid4()
        territory_id = uuid4()
        user1 = uuid4()
        user2 = uuid4()

        mock_member_repository.get_member_user_ids.return_value = [user1, user2]
        mock_split_rate_repository.delete_by_territory.return_value = 1

        await sync_service.sync_team_to_territory(team_id, territory_id)

        mock_split_rate_repository.delete_by_territory.assert_called_once_with(
            territory_id
        )
        assert mock_split_rate_repository.create.call_count == 2

    @pytest.mark.asyncio
    async def test_sync_territory_to_team_replaces_team_members(
        self,
        sync_service: "SalesTeamSyncService",
        mock_member_repository: AsyncMock,
        mock_split_rate_repository: AsyncMock,
    ) -> None:
        """Test sync_territory_to_team replaces team members."""
        team_id = uuid4()
        territory_id = uuid4()
        user1 = uuid4()

        mock_rate = MagicMock()
        mock_rate.user_id = user1
        mock_split_rate_repository.get_by_territory.return_value = [mock_rate]
        mock_member_repository.delete_by_sales_team.return_value = 2

        await sync_service.sync_territory_to_team(territory_id, team_id)

        mock_member_repository.delete_by_sales_team.assert_called_once_with(team_id)
        mock_member_repository.create.assert_called_once()


class TestSalesTeamFilterStrategy:
    """Tests for SalesTeamFilterStrategy RBAC filtering."""

    def test_strategy_resource_property(self) -> None:
        """Test strategy returns correct resource."""
        from commons.db.v6 import RbacResourceEnum

        from app.graphql.v2.rbac.strategies.sales_team_filter import (
            SalesTeamFilterStrategy,
        )

        mock_column = MagicMock()
        strategy = SalesTeamFilterStrategy(
            resource=RbacResourceEnum.CUSTOMER,
            created_by_column=mock_column,
        )

        assert strategy.resource == RbacResourceEnum.CUSTOMER

    def test_strategy_accepts_created_by_column(self) -> None:
        """Test strategy constructor accepts created_by_column."""
        from commons.db.v6 import RbacResourceEnum

        from app.graphql.v2.rbac.strategies.sales_team_filter import (
            SalesTeamFilterStrategy,
        )

        mock_column = MagicMock()
        strategy = SalesTeamFilterStrategy(
            resource=RbacResourceEnum.QUOTE,
            created_by_column=mock_column,
        )

        assert strategy._created_by_column == mock_column
