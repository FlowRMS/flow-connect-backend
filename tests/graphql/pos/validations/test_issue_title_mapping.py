from app.graphql.pos.validations.constants import get_issue_title


class TestIssueTitleMapping:
    def test_required_field_selling_branch_zip_title(self) -> None:
        """Returns human-readable title for missing selling branch zip."""
        title = get_issue_title("required_field", "selling_branch_zip_code")
        assert title == "Selling branch zip code missing"

    def test_required_field_product_identifier_title(self) -> None:
        """Returns human-readable title for missing product identifier."""
        title = get_issue_title("required_field", "manufacturer_catalog_number")
        assert title == "No product identifier found"

    def test_zip_code_validation_title(self) -> None:
        """Returns human-readable title for invalid zip code format."""
        title = get_issue_title("zip_code", "selling_branch_zip_code")
        assert title == "Invalid ZIP code format"

    def test_unknown_combination_fallback(self) -> None:
        """Returns sensible fallback for unmapped combinations."""
        title = get_issue_title("unknown_key", "unknown_column")
        assert "unknown_key" in title.lower() or "validation" in title.lower()
