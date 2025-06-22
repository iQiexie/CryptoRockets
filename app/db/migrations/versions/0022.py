"""refactor gifts

Revision ID: 0022
Revises: 0021
Create Date: 2025-06-21 18:37:51.379985

"""
from alembic import op
import sqlalchemy as sa


revision = '0022'
down_revision = '0021'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing foreign key constraint first
    op.drop_constraint('bets_config_collection_id_fkey', 'bets_config', type_='foreignkey')

    # Drop the old 'collection_id' column
    op.drop_column('bets_config', 'collection_id')

    # Create new 'collection_id' column with the new type (String)
    op.add_column('bets_config', sa.Column('collection_id', sa.String(), nullable=True))

    # Create a new foreign key constraint referencing 'collections.slug'
    op.create_foreign_key(
        'bets_config_collections_fkey', 'bets_config', 'collections', ['collection_id'], ['slug']
        )


def downgrade() -> None:
    # Drop new foreign key constraint
    op.drop_constraint('bets_config_collections_fkey', 'bets_config', type_='foreignkey')

    # Drop the new 'collection_id' column
    op.drop_column('bets_config', 'collection_id')

    # Recreate the old 'collection_id' column (BIGINT)
    op.add_column('bets_config', sa.Column('collection_id', sa.BigInteger(), nullable=True))

    # Restore the original foreign key constraint referencing 'collections.id'
    op.create_foreign_key(
        'bets_config_collection_id_fkey', 'bets_config', 'collections', ['collection_id'], ['id']
        )
