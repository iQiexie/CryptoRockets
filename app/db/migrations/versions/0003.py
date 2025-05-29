"""add wheel winners

Revision ID: 0003
Revises: 0002
Create Date: 2025-05-29 14:29:32.576902

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'wheel_prizes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('amount', sa.Numeric(), nullable=True),
        sa.Column('icon', sa.String(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
        sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    op.drop_table('wheel_prizes')
