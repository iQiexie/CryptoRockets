"""add tables

Revision ID: 0001
Revises:
Create Date: 2025-05-27 18:38:00.933832

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("tg_username", sa.String(), nullable=True),
        sa.Column("tg_first_name", sa.String(), nullable=True),
        sa.Column("tg_last_name", sa.String(), nullable=True),
        sa.Column("tg_is_premium", sa.Boolean(), nullable=True),
        sa.Column("tg_language_code", sa.String(), nullable=True),
        sa.Column("tg_photo_url", sa.String(), nullable=True),
        sa.Column("bot_banned", sa.Boolean(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("ton_balance", sa.Numeric(), server_default="0", nullable=False),
        sa.Column("usdt_balance", sa.Numeric(), server_default="0", nullable=False),
        sa.Column("token_balance", sa.Numeric(), server_default="0", nullable=False),
        sa.Column("fuel_balance", sa.Numeric(), server_default="0", nullable=False),
        sa.Column("wheel_balance", sa.Numeric(), server_default="0", nullable=False),
        sa.Column("referral_from", sa.String(), nullable=True),
        sa.Column("referral", sa.String(), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_id"),
    )

    op.create_table(
        "rockets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("fuel_capacity", sa.Integer(), nullable=False),
        sa.Column("current_fuel", sa.Integer(), server_default="0", nullable=False),
        sa.Column("count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("balance_before", sa.Numeric(), nullable=True),
        sa.Column("balance_after", sa.Numeric(), nullable=True),
        sa.Column("balance_amount", sa.Numeric(), nullable=True),
        sa.Column("balance_currency", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("refund_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["refund_id"],
            ["transactions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.telegram_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("rockets")
    op.drop_table("users")
