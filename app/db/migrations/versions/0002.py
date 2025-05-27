"""add tasks

Revision ID: 0002
Revises: 0001
Create Date: 2025-05-27 20:35:22.336874

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('reward', sa.String(), nullable=False),
        sa.Column('reward_amount', sa.Numeric(), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
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
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_users_task_id'), 'tasks_users', ['task_id'], unique=False)
    op.create_index(op.f('ix_tasks_users_user_id'), 'tasks_users', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_tasks_users_user_id'), table_name='tasks_users')
    op.drop_index(op.f('ix_tasks_users_task_id'), table_name='tasks_users')
    op.drop_table('tasks_users')
    op.drop_table('tasks')
