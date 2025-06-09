"""add task_icon

Revision ID: 0003
Revises: 0002
Create Date: 2025-06-04 08:36:46.537642

"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("icon", sa.String(), nullable=True))
    op.add_column("tasks", sa.Column("name", sa.String(), nullable=True))

    op.execute("UPDATE tasks SET icon = 'default_icon' WHERE icon IS NULL")
    op.execute("UPDATE tasks SET name = 'default_name' WHERE name IS NULL")

    op.alter_column("tasks", "icon", nullable=False)
    op.alter_column("tasks", "name", nullable=False)


def downgrade() -> None:
    op.drop_column("tasks", "name")
    op.drop_column("tasks", "icon")
