"""add last_broadcast_key

Revision ID: 0008
Revises: 0007
Create Date: 2025-05-31 11:40:35.734784

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('last_broadcast_key', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_broadcast_key')
