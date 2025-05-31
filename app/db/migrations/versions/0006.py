"""add check if subscribed

Revision ID: 0006
Revises: 0005
Create Date: 2025-05-31 10:56:26.458256

"""
import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("telegram_id", sa.BigInteger(), nullable=True))
    op.create_unique_constraint("tasks_users_user_id_task_id_unique_key", "tasks_users", ["user_id", "task_id"])


def downgrade() -> None:
    op.drop_constraint("tasks_users_user_id_task_id_unique_key", "tasks_users", type_="unique")
    op.drop_column("tasks", "telegram_id")
