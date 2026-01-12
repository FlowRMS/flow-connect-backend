from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f607"
down_revision: str = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create shipment_requests table
    if not inspector.has_table("shipment_requests", schema="pywarehouse"):
        _ = op.create_table(
            "shipment_requests",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("request_number", sa.String(100), nullable=False, unique=True),
            sa.Column(
                "warehouse_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pywarehouse.warehouses.id"),
                nullable=True,
                index=True,
            ),
            sa.Column(
                "customer_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pycore.customers.id"),
                nullable=True,
                index=True,
            ),
            sa.Column(
                "factory_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pycore.factories.id"),
                nullable=True,
            ),
            # IntEnum stored as Integer
            sa.Column("method", sa.Integer, nullable=True),
            sa.Column("priority", sa.Integer, nullable=False, default=1),
            sa.Column("status", sa.Integer, nullable=False, default=1),
            sa.Column("request_date", sa.DateTime(timezone=False), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=False, default=True),
            sa.Column("notes", sa.String(), nullable=True),
            # Audit columns
            sa.Column(
                "created_by_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pyuser.users.id"),
                nullable=True,
                index=True,
            ),
            sa.Column(
                "created_at", sa.DateTime(timezone=False), server_default=sa.func.now()
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=False),
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
            ),
            schema="pywarehouse",
        )

    # Create shipment_request_items table
    if not inspector.has_table("shipment_request_items", schema="pywarehouse"):
        _ = op.create_table(
            "shipment_request_items",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column(
                "request_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pywarehouse.shipment_requests.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "product_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pycore.products.id"),
                nullable=False,
                index=True,
            ),
            # Quantity as Numeric to match Decimal in model
            sa.Column("quantity", sa.Numeric, nullable=False, default=1),
            # Audit columns
            sa.Column(
                "created_by_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pyuser.users.id"),
                nullable=True,
                index=True,
            ),
            sa.Column(
                "created_at", sa.DateTime(timezone=False), server_default=sa.func.now()
            ),
            schema="pywarehouse",
        )


def downgrade() -> None:
    op.drop_table("shipment_request_items", schema="pywarehouse")
    op.drop_table("shipment_requests", schema="pywarehouse")
