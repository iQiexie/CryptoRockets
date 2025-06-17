"""add bets

Revision ID: 0008
Revises: 0007
Create Date: 2025-06-17 23:58:19.078155

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'gifts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('fragment', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('image', sa.String(), nullable=False),
        sa.Column('avg_price', sa.Numeric(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('fragment')
        )

    op.create_table(
        'bets_config',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('gift_id', sa.BigInteger(), nullable=True),
        sa.Column('bet_from', sa.Numeric(), nullable=False),
        sa.Column('probability', sa.Numeric(), nullable=False),
        sa.Column('actual_probability', sa.Numeric(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['gift_id'], ['gifts.id'], ),
        sa.PrimaryKeyConstraint('id')
        )

    op.create_index(op.f('ix_bets_config_gift_id'), 'bets_config', ['gift_id'], unique=False)
    op.create_table(
        'gifts_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('gift_id', sa.BigInteger(), nullable=True),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['gift_id'], ['gifts.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
        sa.PrimaryKeyConstraint('id')
        )

    op.create_index(op.f('ix_gifts_users_gift_id'), 'gifts_users', ['gift_id'], unique=False)
    op.create_index(op.f('ix_gifts_users_user_id'), 'gifts_users', ['user_id'], unique=False)
    op.add_column('rockets', sa.Column('transaction_id', sa.Integer(), nullable=True))
    op.create_foreign_key('rockets_transactions_fkey', 'rockets', 'transactions', ['transaction_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('rockets_transactions_fkey', 'rockets', type_='foreignkey')
    op.drop_column('rockets', 'transaction_id')
    op.drop_index(op.f('ix_gifts_users_user_id'), table_name='gifts_users')
    op.drop_index(op.f('ix_gifts_users_gift_id'), table_name='gifts_users')
    op.drop_table('gifts_users')
    op.drop_index(op.f('ix_bets_config_gift_id'), table_name='bets_config')
    op.drop_table('bets_config')
    op.drop_table('gifts')
