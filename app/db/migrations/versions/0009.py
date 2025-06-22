"""add gifts

Revision ID: 0009
Revises: 0008
Create Date: 2025-06-18 22:04:31.157931

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0009'
down_revision = '0008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'collections',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('image', sa.String(), nullable=False),
        sa.Column('avg_price', sa.Numeric(), nullable=True),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_table(
        'bets_config',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('collection_id', sa.BigInteger(), nullable=True),
        sa.Column('bet_from', sa.Numeric(), nullable=False),
        sa.Column('probability', sa.Numeric(), nullable=False),
        sa.Column('actual_probability', sa.Numeric(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bets_config_collection_id'), 'bets_config', ['collection_id'], unique=False)
    op.create_table(
        'gifts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('collection_id', sa.String(), nullable=False),
        sa.Column('transfer_date', postgresql.TIMESTAMP(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('gift_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('price_purchase', sa.Numeric(), nullable=True),
        sa.Column('price_release', sa.Numeric(), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['collection_id'], ['collections.slug'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address'),
        sa.UniqueConstraint('gift_id')
    )
    op.create_table(
        'gifts_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('gift_id', sa.Integer(), nullable=True),
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


def downgrade() -> None:
    op.drop_index(op.f('ix_gifts_users_user_id'), table_name='gifts_users')
    op.drop_index(op.f('ix_gifts_users_gift_id'), table_name='gifts_users')
    op.drop_table('gifts_users')
    op.drop_table('gifts')
    op.drop_index(op.f('ix_bets_config_collection_id'), table_name='bets_config')
    op.drop_table('bets_config')
    op.drop_table('collections')
