"""add_weight_to_days

Revision ID: 0df93e546a3f
Revises: 4af5afb594b6
Create Date: 2025-11-07 20:26:16.098889

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0df93e546a3f'
down_revision: Union[str, None] = '4af5afb594b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add weight column to days table
    op.add_column('days', sa.Column('weight', sa.Numeric(precision=5, scale=2), nullable=True))


def downgrade() -> None:
    # Remove weight column from days table
    op.drop_column('days', 'weight')
