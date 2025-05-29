"""add rocket skins

Revision ID: 0005
Revises: 0004
Create Date: 2025-05-29 20:12:06.021650

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("invoices", sa.Column("rocket_skin", sa.String(), nullable=True))
    op.add_column(
        "rockets",
        sa.Column("skins", postgresql.JSONB(astext_type=sa.Text()), server_default='["default"]', nullable=False),
    )
    op.add_column("rockets", sa.Column("current_skin", sa.String(), server_default='"default"', nullable=False))


def downgrade() -> None:
    op.drop_column("rockets", "current_skin")
    op.drop_column("rockets", "skins")
    op.drop_column("invoices", "rocket_skin")
