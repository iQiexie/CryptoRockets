"""add rockets_transactions_fkey

Revision ID: 0008
Revises: 0007
Create Date: 2025-06-18 20:48:35.450992

"""
from alembic import op
import sqlalchemy as sa

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('rockets', sa.Column('transaction_id', sa.Integer(), nullable=True))
    op.create_foreign_key('rockets_transactions_fkey', 'rockets', 'transactions', ['transaction_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('rockets_transactions_fkey', 'rockets', type_='foreignkey')
    op.drop_column('rockets', 'transaction_id')
