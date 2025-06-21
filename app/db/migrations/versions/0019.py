"""refactor gifts

Revision ID: 0019
Revises: 0018
Create Date: 2025-06-21 17:22:13.130968

"""
from alembic import op
import sqlalchemy as sa


revision = '0019'
down_revision = '0018'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old constraint if exists
    op.drop_constraint('gifts_users_collections_fkey', 'gifts_users', type_='foreignkey')

    # Drop the old column
    op.drop_column('gifts_users', 'collection_id')

    # Create the new column with correct type (string) and foreign key constraint
    op.add_column('gifts_users', sa.Column('collection_id', sa.String(), nullable=True))

    op.create_foreign_key(
        'gifts_users_collections_fkey',
        'gifts_users',
        'collections',
        ['collection_id'],
        ['slug']
    )

    op.alter_column('gifts_users', 'roll_id',
               existing_type=sa.INTEGER(),
               nullable=True)



def downgrade() -> None:
    # Drop the new foreign key constraint
    op.drop_constraint('gifts_users_collections_fkey', 'gifts_users', type_='foreignkey')

    # Drop the new column
    op.drop_column('gifts_users', 'collection_id')

    # Recreate the old column with previous type (BIGINT)
    op.add_column('gifts_users', sa.Column('collection_id', sa.BIGINT(), nullable=True))

    # Recreate the old foreign key constraint (assuming it referenced collections.id)
    op.create_foreign_key(
        'gifts_users_collections_fkey',
        'gifts_users',
        'collections',
        ['collection_id'],
        ['id']
    )

    # Reverse the roll_id alteration if needed; assuming nullable was changed to True during upgrade,
    # revert it to NOT NULL if that was the previous state. Adjust if you know the original.
    op.alter_column('gifts_users', 'roll_id',
               existing_type=sa.INTEGER(),
               nullable=False)
