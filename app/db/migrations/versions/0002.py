"""add invite task

Revision ID: 0002
Revises: 0001
Create Date: 2025-05-31 12:38:01.986682

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('amount', sa.Numeric(), nullable=True))
    op.alter_column('tasks', 'url',
               existing_type=sa.VARCHAR(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('tasks', 'url',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('tasks', 'amount')
