"""init

Revision ID: 0001
Revises: 
Create Date: 2025-05-31 12:07:00.970497

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('reward', sa.String(), nullable=False),
        sa.Column('reward_amount', sa.Numeric(), nullable=False),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('tg_username', sa.String(), nullable=True),
        sa.Column('tg_first_name', sa.String(), nullable=True),
        sa.Column('tg_last_name', sa.String(), nullable=True),
        sa.Column('tg_is_premium', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('tg_language_code', sa.String(), nullable=True),
        sa.Column('tg_photo_url', sa.String(), nullable=True),
        sa.Column('bot_banned', sa.Boolean(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('ton_balance', sa.Numeric(), server_default='0', nullable=False),
        sa.Column('usdt_balance', sa.Numeric(), server_default='0', nullable=False),
        sa.Column('token_balance', sa.Numeric(), server_default='0', nullable=False),
        sa.Column('fuel_balance', sa.Numeric(), server_default='0', nullable=False),
        sa.Column('wheel_balance', sa.Numeric(), server_default='0', nullable=False),
        sa.Column('last_broadcast_key', sa.String(), nullable=True),
        sa.Column('referral_from', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['referral_from'], ['users.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index(op.f('ix_users_referral_from'), 'users', ['referral_from'], unique=False)
    op.create_table(
        'rockets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('fuel_capacity', sa.Integer(), nullable=False),
        sa.Column('current_fuel', sa.Integer(), server_default='0', nullable=False),
        sa.Column('count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column(
            'skins', postgresql.JSONB(astext_type=sa.Text()), server_default='["default"]', nullable=False
            ),
        sa.Column('current_skin', sa.String(), server_default='"default"', nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table(
        'tasks_users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'task_id')
    )
    op.create_index(op.f('ix_tasks_users_task_id'), 'tasks_users', ['task_id'], unique=False)
    op.create_index(op.f('ix_tasks_users_user_id'), 'tasks_users', ['user_id'], unique=False)
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('balance_before', sa.Numeric(), nullable=True),
        sa.Column('balance_after', sa.Numeric(), nullable=True),
        sa.Column('balance_amount', sa.Numeric(), nullable=True),
        sa.Column('balance_currency', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('refund_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['refund_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'wheel_prizes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('amount', sa.Numeric(), nullable=True),
        sa.Column('icon', sa.String(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('currency_amount', sa.Numeric(), nullable=False),
        sa.Column('currency_fee', sa.Numeric(), server_default='0', nullable=False),
        sa.Column('usd_amount', sa.Numeric(), nullable=False),
        sa.Column('transaction_id', sa.Integer(), nullable=True),
        sa.Column('rocket_id', sa.Integer(), nullable=True),
        sa.Column('rocket_skin', sa.String(), nullable=True),
        sa.Column('callback_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('refunded', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['rocket_id'], ['rockets.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.telegram_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_table('invoices')
    op.drop_table('wheel_prizes')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_tasks_users_user_id'), table_name='tasks_users')
    op.drop_index(op.f('ix_tasks_users_task_id'), table_name='tasks_users')
    op.drop_table('tasks_users')
    op.drop_table('rockets')
    op.drop_index(op.f('ix_users_referral_from'), table_name='users')
    op.drop_table('users')
    op.drop_table('tasks')
