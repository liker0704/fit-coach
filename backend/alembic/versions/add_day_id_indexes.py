"""Add indexes on day_id foreign keys for better query performance

Revision ID: add_day_id_indexes
Revises: add_unique_user_date
Create Date: 2025-11-18 17:05:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_day_id_indexes'
down_revision = 'add_unique_user_date'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes on day_id columns in related tables."""
    # Add index on meals.day_id
    op.create_index(
        op.f('ix_meals_day_id'),
        'meals',
        ['day_id'],
        unique=False
    )

    # Add index on exercises.day_id
    op.create_index(
        op.f('ix_exercises_day_id'),
        'exercises',
        ['day_id'],
        unique=False
    )

    # Add index on water_intakes.day_id
    op.create_index(
        op.f('ix_water_intakes_day_id'),
        'water_intakes',
        ['day_id'],
        unique=False
    )

    # Add index on sleep_records.day_id
    op.create_index(
        op.f('ix_sleep_records_day_id'),
        'sleep_records',
        ['day_id'],
        unique=False
    )

    # Add index on mood_records.day_id
    op.create_index(
        op.f('ix_mood_records_day_id'),
        'mood_records',
        ['day_id'],
        unique=False
    )

    # Add index on notes.day_id
    op.create_index(
        op.f('ix_notes_day_id'),
        'notes',
        ['day_id'],
        unique=False
    )


def downgrade():
    """Remove indexes from day_id columns."""
    op.drop_index(op.f('ix_notes_day_id'), table_name='notes')
    op.drop_index(op.f('ix_mood_records_day_id'), table_name='mood_records')
    op.drop_index(op.f('ix_sleep_records_day_id'), table_name='sleep_records')
    op.drop_index(op.f('ix_water_intakes_day_id'), table_name='water_intakes')
    op.drop_index(op.f('ix_exercises_day_id'), table_name='exercises')
    op.drop_index(op.f('ix_meals_day_id'), table_name='meals')
