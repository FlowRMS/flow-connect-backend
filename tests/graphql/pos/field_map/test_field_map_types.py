import uuid

import strawberry

from app.graphql.pos.field_map.models.field_map_config import DEFAULT_FIELDS
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldMapDirection,
    FieldMapType,
)
from app.graphql.pos.field_map.strawberry.field_map_types import (
    FieldMapFieldResponse,
    FieldMapResponse,
)


class TestFieldMapResponseFromDefaults:
    """Tests for FieldMapResponse.from_defaults() factory method."""

    def test_from_defaults_has_null_id(self) -> None:
        """Virtual response has id=None."""
        response = FieldMapResponse.from_defaults(
            organization_id=None,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.SEND,
        )

        assert response.id is None

    def test_from_defaults_has_all_default_fields(self) -> None:
        """Contains all default fields from config."""
        response = FieldMapResponse.from_defaults(
            organization_id=None,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.SEND,
        )

        assert len(response.fields) == len(DEFAULT_FIELDS)

    def test_from_defaults_fields_have_null_id(self) -> None:
        """Each virtual field has id=None."""
        response = FieldMapResponse.from_defaults(
            organization_id=None,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.SEND,
        )

        for field in response.fields:
            assert field.id is None

    def test_from_defaults_includes_categories(self) -> None:
        """Categories are populated with all 8 categories."""
        response = FieldMapResponse.from_defaults(
            organization_id=None,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.SEND,
        )

        assert len(response.categories) == 8

    def test_from_defaults_respects_map_type(self) -> None:
        """Response has correct map_type."""
        response = FieldMapResponse.from_defaults(
            organization_id=None,
            map_type=FieldMapType.POT,
            direction=FieldMapDirection.SEND,
        )

        assert response.map_type == FieldMapType.POT

    def test_from_defaults_respects_direction(self) -> None:
        """Response has correct direction."""
        response = FieldMapResponse.from_defaults(
            organization_id=None,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.RECEIVE,
        )

        assert response.direction == FieldMapDirection.RECEIVE

    def test_from_defaults_respects_organization_id(self) -> None:
        """Response has correct organization_id."""
        org_id = uuid.uuid4()

        response = FieldMapResponse.from_defaults(
            organization_id=org_id,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.SEND,
        )

        assert response.organization_id == strawberry.ID(str(org_id))

    def test_from_defaults_null_organization_id(self) -> None:
        """Response has None for global defaults."""
        response = FieldMapResponse.from_defaults(
            organization_id=None,
            map_type=FieldMapType.POS,
            direction=FieldMapDirection.SEND,
        )

        assert response.organization_id is None


class TestFieldMapFieldResponseFromDefaultConfig:
    """Tests for FieldMapFieldResponse.from_default_config() factory method."""

    def test_from_default_config_has_null_id(self) -> None:
        """Virtual field has id=None."""
        config = DEFAULT_FIELDS[0]

        response = FieldMapFieldResponse.from_default_config(config)

        assert response.id is None

    def test_from_default_config_has_correct_key(self) -> None:
        """Field has correct standard_field_key from config."""
        config = DEFAULT_FIELDS[0]

        response = FieldMapFieldResponse.from_default_config(config)

        assert response.standard_field_key == config.key

    def test_from_default_config_is_default_true(self) -> None:
        """Virtual field from config has is_default=True."""
        config = DEFAULT_FIELDS[0]

        response = FieldMapFieldResponse.from_default_config(config)

        assert response.is_default is True

    def test_from_default_config_not_linked(self) -> None:
        """Virtual field from config is not linked."""
        config = DEFAULT_FIELDS[0]

        response = FieldMapFieldResponse.from_default_config(config)

        assert response.linked is False
        assert response.organization_field_name is None
