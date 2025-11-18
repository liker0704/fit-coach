"""Add unique constraint on user_id and date in days table

Revision ID: add_unique_user_date
Revises: add_training_programs
Create Date: 2025-11-18 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_unique_user_date'
down_revision = 'add_training_programs'
branch_labels = None
depends_on = None


def upgrade():
    """Add unique constraint on (user_id, date) to days table."""
    # Create unique constraint to ensure one day per user per date
    op.create_unique_constraint(
        'uq_user_date',
        'days',
        ['user_id', 'date']
    )


def downgrade():
    """Remove unique constraint from days table."""
    op.drop_constraint('uq_user_date', 'days', type_='unique')
