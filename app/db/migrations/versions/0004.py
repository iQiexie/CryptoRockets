"""add shop

Revision ID: 0004
Revises: 0003
Create Date: 2025-05-29 18:58:48.319691

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("currency_amount", sa.Numeric(), nullable=False),
        sa.Column("currency_fee", sa.Numeric(), server_default="0", nullable=False),
        sa.Column("usd_amount", sa.Numeric(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.Column("rocket_id", sa.Integer(), nullable=True),
        sa.Column("callback_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("refunded", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["rocket_id"],
            ["rockets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["transactions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.telegram_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )


def downgrade() -> None:
    op.drop_table("invoices")
