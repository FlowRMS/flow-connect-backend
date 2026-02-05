from decimal import Decimal
from uuid import uuid4

from app.graphql.statements.strawberry.statement_detail_input import (
    StatementDetailInput,
)


class TestStatementDetailInputToOrmModel:
    """Tests for StatementDetailInput.to_orm_model() commission calculation logic."""

    def test_commission_calculated_from_rate_when_no_commission_provided(self) -> None:
        """Commission should be calculated from rate when no direct commission value is provided."""
        detail_input = StatementDetailInput(
            item_number=1,
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            commission_rate=Decimal("5"),
            discount_rate=Decimal("0"),
            commission_discount_rate=Decimal("0"),
        )

        result = detail_input.to_orm_model()

        # quantity * unit_price = 10 * 100 = 1000 (subtotal)
        # subtotal - discount = 1000 - 0 = 1000 (total)
        # commission = total * (rate / 100) = 1000 * 0.05 = 50
        assert result.subtotal == Decimal("1000")
        assert result.total == Decimal("1000")
        assert result.commission == Decimal("50")
        assert result.commission_rate == Decimal("5")

    def test_commission_pass_through_when_commission_provided(self) -> None:
        """Commission should use the provided value directly when specified (pass-through mode)."""
        detail_input = StatementDetailInput(
            item_number=1,
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            commission_rate=Decimal("5"),  # This should be ignored for commission calculation
            discount_rate=Decimal("0"),
            commission_discount_rate=Decimal("0"),
            commission=Decimal("75"),  # Direct commission value
        )

        result = detail_input.to_orm_model()

        # Commission should be the pass-through value, not calculated from rate
        assert result.commission == Decimal("75")
        # Rate should still be stored as provided
        assert result.commission_rate == Decimal("5")
        # total_line_commission = commission - commission_discount = 75 - 0 = 75
        assert result.total_line_commission == Decimal("75")

    def test_commission_pass_through_overrides_rate_calculation(self) -> None:
        """When commission is provided, it should completely override rate-based calculation."""
        detail_input = StatementDetailInput(
            item_number=1,
            quantity=Decimal("100"),
            unit_price=Decimal("50"),
            commission_rate=Decimal("10"),  # Would calculate to 500
            discount_rate=Decimal("0"),
            commission_discount_rate=Decimal("0"),
            commission=Decimal("123.45"),  # Pass-through value
        )

        result = detail_input.to_orm_model()

        # Without pass-through: 100 * 50 * 0.10 = 500
        # With pass-through: should be exactly 123.45
        assert result.commission == Decimal("123.45")
        assert result.total_line_commission == Decimal("123.45")

    def test_commission_pass_through_with_commission_discount(self) -> None:
        """Commission discount should be applied to pass-through commission."""
        detail_input = StatementDetailInput(
            item_number=1,
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            commission_rate=Decimal("5"),
            discount_rate=Decimal("0"),
            commission_discount_rate=Decimal("10"),  # 10% commission discount
            commission=Decimal("100"),  # Pass-through commission
        )

        result = detail_input.to_orm_model()

        # commission = 100 (pass-through)
        # commission_discount = 100 * (10 / 100) = 10
        # total_line_commission = 100 - 10 = 90
        assert result.commission == Decimal("100")
        assert result.commission_discount == Decimal("10")
        assert result.total_line_commission == Decimal("90")

    def test_rate_based_commission_with_discount(self) -> None:
        """Rate-based commission calculation should work correctly with product discount."""
        detail_input = StatementDetailInput(
            item_number=1,
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            discount_rate=Decimal("20"),  # 20% product discount
            commission_rate=Decimal("5"),
            commission_discount_rate=Decimal("0"),
        )

        result = detail_input.to_orm_model()

        # subtotal = 10 * 100 = 1000
        # discount = 1000 * 0.20 = 200
        # total = 1000 - 200 = 800
        # commission = 800 * 0.05 = 40
        assert result.subtotal == Decimal("1000")
        assert result.discount == Decimal("200")
        assert result.total == Decimal("800")
        assert result.commission == Decimal("40")
        assert result.total_line_commission == Decimal("40")

    def test_rate_based_commission_with_both_discounts(self) -> None:
        """Rate-based commission with both product discount and commission discount."""
        detail_input = StatementDetailInput(
            item_number=1,
            quantity=Decimal("20"),
            unit_price=Decimal("50"),
            discount_rate=Decimal("10"),  # 10% product discount
            commission_rate=Decimal("8"),
            commission_discount_rate=Decimal("5"),  # 5% commission discount
        )

        result = detail_input.to_orm_model()

        # subtotal = 20 * 50 = 1000
        # discount = 1000 * 0.10 = 100
        # total = 1000 - 100 = 900
        # commission = 900 * 0.08 = 72
        # commission_discount = 72 * 0.05 = 3.60
        # total_line_commission = 72 - 3.60 = 68.40
        assert result.subtotal == Decimal("1000")
        assert result.discount == Decimal("100")
        assert result.total == Decimal("900")
        assert result.commission == Decimal("72")
        assert result.commission_discount == Decimal("3.60")
        assert result.total_line_commission == Decimal("68.40")

    def test_zero_commission_pass_through(self) -> None:
        """Zero commission should be respected as a valid pass-through value."""
        detail_input = StatementDetailInput(
            item_number=1,
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            commission_rate=Decimal("5"),  # Would normally calculate to 50
            discount_rate=Decimal("0"),
            commission_discount_rate=Decimal("0"),
            commission=Decimal("0"),  # Explicitly zero commission
        )

        result = detail_input.to_orm_model()

        # Zero commission should be used even though rate would calculate to 50
        assert result.commission == Decimal("0")
        assert result.total_line_commission == Decimal("0")

    def test_commission_none_falls_back_to_rate_calculation(self) -> None:
        """When commission is None (default), rate-based calculation should be used."""
        detail_input = StatementDetailInput(
            item_number=1,
            quantity=Decimal("5"),
            unit_price=Decimal("200"),
            commission_rate=Decimal("4"),
            discount_rate=Decimal("0"),
            commission_discount_rate=Decimal("0"),
            # commission is not provided (defaults to None)
        )

        result = detail_input.to_orm_model()

        # subtotal = 5 * 200 = 1000
        # commission = 1000 * 0.04 = 40
        assert result.commission == Decimal("40")
        assert result.total_line_commission == Decimal("40")

    def test_orm_model_retains_id_when_provided(self) -> None:
        """When ID is provided, it should be set on the resulting ORM model."""
        existing_id = uuid4()
        detail_input = StatementDetailInput(
            id=existing_id,
            item_number=1,
            quantity=Decimal("1"),
            unit_price=Decimal("100"),
        )

        result = detail_input.to_orm_model()

        assert result.id == existing_id

    def test_orm_model_all_fields_populated(self) -> None:
        """Verify all fields are properly populated on the ORM model."""
        sold_to_id = uuid4()
        order_id = uuid4()
        product_id = uuid4()
        end_user_id = uuid4()

        detail_input = StatementDetailInput(
            item_number=5,
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            sold_to_customer_id=sold_to_id,
            order_id=order_id,
            product_id=product_id,
            product_name_adhoc="Test Product",
            product_description_adhoc="Test Description",
            end_user_id=end_user_id,
            lead_time="2-3 weeks",
            note="Test note",
            discount_rate=Decimal("5"),
            commission_rate=Decimal("10"),
            commission_discount_rate=Decimal("2"),
            commission=Decimal("95"),  # Pass-through
        )

        result = detail_input.to_orm_model()

        assert result.item_number == 5
        assert result.quantity == Decimal("10")
        assert result.unit_price == Decimal("100")
        assert result.sold_to_customer_id == sold_to_id
        assert result.order_id == order_id
        assert result.product_id == product_id
        assert result.product_name_adhoc == "Test Product"
        assert result.product_description_adhoc == "Test Description"
        assert result.end_user_id == end_user_id
        assert result.lead_time == "2-3 weeks"
        assert result.note == "Test note"
        assert result.discount_rate == Decimal("5")
        assert result.commission_rate == Decimal("10")
        assert result.commission_discount_rate == Decimal("2")
        assert result.commission == Decimal("95")
