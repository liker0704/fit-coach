"""rename_metadata_to_meta_data

Revision ID: 4af5afb594b6
Revises: 4232ee534200
Create Date: 2025-11-02 22:30:44.311548

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4af5afb594b6'
down_revision: Union[str, None] = '4232ee534200'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename metadata to meta_data in agent_memories table
    op.alter_column('agent_memories', 'metadata', new_column_name='meta_data')
    
    # Rename metadata to meta_data in agent_conversations table
    op.alter_column('agent_conversations', 'metadata', new_column_name='meta_data')


def downgrade() -> None:
    # Revert meta_data back to metadata in agent_conversations table
    op.alter_column('agent_conversations', 'meta_data', new_column_name='metadata')
    
    # Revert meta_data back to metadata in agent_memories table
    op.alter_column('agent_memories', 'meta_data', new_column_name='metadata')
