"""Add timezone support to remaining datetime columns

Revision ID: add_tz_remaining_dt
Revises: add_day_id_indexes
Create Date: 2025-11-18 17:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_tz_remaining_dt'
down_revision = 'add_day_id_indexes'
branch_labels = None
depends_on = None


def upgrade():
    """Add timezone support to remaining DateTime columns."""
    # Meals table
    op.alter_column(
        'meals',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    # Exercises table
    op.alter_column(
        'exercises',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    op.alter_column(
        'exercises',
        'start_time',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True
    )

    # Water intakes table
    op.alter_column(
        'water_intakes',
        'time',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    # Sleep records table
    op.alter_column(
        'sleep_records',
        'bedtime',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True
    )

    op.alter_column(
        'sleep_records',
        'wake_time',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True
    )

    # Mood records table
    op.alter_column(
        'mood_records',
        'time',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    # Notes table
    op.alter_column(
        'notes',
        'updated_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True
    )


def downgrade():
    """Remove timezone support from DateTime columns."""
    # Notes table
    op.alter_column(
        'notes',
        'updated_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True
    )

    # Mood records table
    op.alter_column(
        'mood_records',
        'time',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    # Sleep records table
    op.alter_column(
        'sleep_records',
        'wake_time',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True
    )

    op.alter_column(
        'sleep_records',
        'bedtime',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True
    )

    # Water intakes table
    op.alter_column(
        'water_intakes',
        'time',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    # Exercises table
    op.alter_column(
        'exercises',
        'start_time',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True
    )

    op.alter_column(
        'exercises',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )

    # Meals table
    op.alter_column(
        'meals',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
        existing_server_default=sa.text('CURRENT_TIMESTAMP')
    )
