"""Add persistent dietary preferences."""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dietary_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("excluded_foods", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_dietary_preferences_user_id", "dietary_preferences", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_dietary_preferences_user_id", table_name="dietary_preferences")
    op.drop_table("dietary_preferences")
