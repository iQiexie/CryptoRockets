"""add ton address

Revision ID: 0006
Revises: 0005
Create Date: 2025-06-09 18:01:45.764660

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('address', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'address')
