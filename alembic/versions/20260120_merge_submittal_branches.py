from collections.abc import Sequence

revision: str = "2adbedfe0eff"
down_revision: str | tuple[str, ...] | None = (
    "submittal_config_001",
    "add_submittal_settings_fields",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
