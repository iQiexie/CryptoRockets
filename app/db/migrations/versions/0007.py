"""fix default premium

Revision ID: 0007
Revises: 0006
Create Date: 2025-05-31 11:29:58.103741

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'users', 'tg_is_premium',
        existing_type=sa.BOOLEAN(),
        nullable=False
    )
    op.create_index(op.f('ix_users_referral_from'), 'users', ['referral_from'], unique=False)
    op.create_unique_constraint('users_referral_unique_key', 'users', ['referral'])
    op.create_foreign_key(
        'users_referral_from_fkey', 'users', 'users', ['referral_from'], ['referral'], ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('users_referral_from_fkey', 'users', type_='foreignkey')
    op.drop_constraint('users_referral_unique_key', 'users', type_='unique')
    op.drop_index(op.f('ix_users_referral_from'), table_name='users')
    op.alter_column(
        'users', 'tg_is_premium',
        existing_type=sa.BOOLEAN(),
        nullable=True
    )
