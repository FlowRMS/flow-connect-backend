from app.graphql.organizations.models.enums import OrgType


class TestOrgTypeGetComplementaryType:
    def test_manufacturer_complementary_type_is_distributor(self) -> None:
        """Manufacturer's complementary type should be distributor."""
        result = OrgType.MANUFACTURER.get_complementary_type()
        assert result == OrgType.DISTRIBUTOR

    def test_distributor_complementary_type_is_manufacturer(self) -> None:
        """Distributor's complementary type should be manufacturer."""
        result = OrgType.DISTRIBUTOR.get_complementary_type()
        assert result == OrgType.MANUFACTURER
