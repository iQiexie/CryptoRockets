"""refactor

Revision ID: 0005
Revises: 0004
Create Date: 2025-06-09 17:40:29.252929

"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "invoices",
        "currency_fee",
        existing_type=sa.NUMERIC(),
        nullable=True,
        existing_server_default=sa.text("'0'::numeric"),
    )


def downgrade() -> None:
    op.alter_column(
        "invoices",
        "currency_fee",
        existing_type=sa.NUMERIC(),
        nullable=False,
        existing_server_default=sa.text("'0'::numeric"),
    )
