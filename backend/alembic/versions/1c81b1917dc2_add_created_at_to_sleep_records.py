"""add_created_at_to_sleep_records

Revision ID: 1c81b1917dc2
Revises: 84d4d3fed9ca
Create Date: 2025-11-01 13:19:31.956693

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c81b1917dc2'
down_revision: Union[str, None] = '84d4d3fed9ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add created_at column to sleep_records table
    op.add_column('sleep_records',
        sa.Column('created_at', sa.DateTime(),
        server_default=sa.text('CURRENT_TIMESTAMP'),
        nullable=False))


def downgrade() -> None:
    # Remove created_at column from sleep_records table
    op.drop_column('sleep_records', 'created_at')
