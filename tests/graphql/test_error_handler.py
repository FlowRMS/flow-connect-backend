import pytest
from graphql import GraphQLError

from app.errors.common_errors import RemoteApiError
from app.graphql.connections.exceptions import UserNotFoundError
from app.graphql.error_handler import should_mask_error
from app.graphql.pos.agreement.exceptions import AgreementNotFoundError
from app.graphql.pos.data_exchange.exceptions import NoPendingFilesError
from app.graphql.pos.field_map.exceptions import CannotDeleteDefaultFieldError
from app.graphql.pos.organization_alias.exceptions import AliasAlreadyExistsError
from app.graphql.pos.validations.exceptions import PrefixPatternNotFoundError
from app.graphql.settings.organization_preferences.exceptions import (
    InvalidApplicationError,
)


class TestShouldMaskError:
    def test_does_not_mask_base_exception(self) -> None:
        original = RemoteApiError("Connection request already exists")
        error = GraphQLError(
            message="Connection request already exists",
            original_error=original,
        )

        assert should_mask_error(error) is False

    def test_masks_non_base_exception(self) -> None:
        original = ValueError("internal db error details")
        error = GraphQLError(
            message="internal db error details",
            original_error=original,
        )

        assert should_mask_error(error) is True

    def test_does_not_mask_error_without_original_error(self) -> None:
        error = GraphQLError(message="Syntax error in query")

        assert should_mask_error(error) is False

    @pytest.mark.parametrize(
        "exception",
        [
            PrefixPatternNotFoundError("Pattern not found"),
            AliasAlreadyExistsError("Alias already exists"),
            NoPendingFilesError("No pending files"),
            AgreementNotFoundError("Agreement not found"),
            CannotDeleteDefaultFieldError("Cannot delete default"),
            InvalidApplicationError("Invalid application"),
            UserNotFoundError("user_123"),
        ],
        ids=[
            "validations",
            "organization_alias",
            "data_exchange",
            "agreement",
            "field_map",
            "organization_preferences",
            "connections",
        ],
    )
    def test_does_not_mask_domain_exception(self, exception: Exception) -> None:
        error = GraphQLError(
            message=str(exception),
            original_error=exception,
        )

        assert should_mask_error(error) is False
