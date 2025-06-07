"""refactor rockets

Revision ID: 0004
Revises: 0003
Create Date: 2025-06-07 14:10:13.567672

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('rockets', 'skins')
    op.drop_column('rockets', 'count')
    op.drop_column('rockets', 'current_skin')


def downgrade() -> None:
    op.add_column('rockets', sa.Column('current_skin', sa.VARCHAR(), server_default=sa.text('\'"default"\'::character varying'), autoincrement=False, nullable=False))
    op.add_column('rockets', sa.Column('count', sa.INTEGER(), server_default=sa.text('1'), autoincrement=False, nullable=False))
    op.add_column('rockets', sa.Column('skins', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text('\'["default"]\'::jsonb'), autoincrement=False, nullable=False))
