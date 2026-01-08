from collections.abc import Sequence

from alembic import op

revision: str = "5a8b3c2d1e0f"
down_revision: str | None = "44932ca0481e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_customers_company_name",
        "customers",
        ["company_name"],
        schema="pycore",
    )
    op.create_unique_constraint(
        "uq_factories_title",
        "factories",
        ["title"],
        schema="pycore",
    )
    op.create_unique_constraint(
        "uq_products_fpn_factory",
        "products",
        ["factory_part_number", "factory_id"],
        schema="pycore",
    )
    op.create_unique_constraint(
        "uq_product_categories_title_factory",
        "product_categories",
        ["title", "factory_id"],
        schema="pycore",
    )
    op.create_unique_constraint(
        "uq_product_uoms_title",
        "product_uoms",
        ["title"],
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_product_uoms_title",
        "product_uoms",
        schema="pycore",
    )
    op.drop_constraint(
        "uq_product_categories_title_factory",
        "product_categories",
        schema="pycore",
    )
    op.drop_constraint(
        "uq_products_fpn_factory",
        "products",
        schema="pycore",
    )
    op.drop_constraint(
        "uq_factories_title",
        "factories",
        schema="pycore",
    )
    op.drop_constraint(
        "uq_customers_company_name",
        "customers",
        schema="pycore",
    )
