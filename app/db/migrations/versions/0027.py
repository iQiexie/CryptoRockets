"""add rich_ads_tasks

Revision ID: 0027
Revises: 0026
Create Date: 2025-06-25 18:44:36.040605

"""
from alembic import op
import sqlalchemy as sa


revision = '0027'
down_revision = '0026'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ads', sa.Column('rocket_type', sa.String(), nullable=True))

    op.add_column('ads', sa.Column('token', sa.String(), nullable=True))
    op.create_unique_constraint('ads_token_uq', 'ads', ['token'])


def downgrade() -> None:
    op.drop_column('ads', 'rocket_type')
    op.drop_constraint('ads_token_uq', 'ads', type_='unique')
    op.drop_column('ads', 'token')
