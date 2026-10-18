"""Add administrator-managed free access grants."""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "free_access_grants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("granted_by", sa.BigInteger(), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_index("ix_free_access_grants_telegram_id", "free_access_grants", ["telegram_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_free_access_grants_telegram_id", table_name="free_access_grants")
    op.drop_table("free_access_grants")
