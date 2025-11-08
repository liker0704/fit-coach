"""add training programs table

Revision ID: add_training_programs
Revises: add_meal_plans
Create Date: 2025-11-08 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = 'add_training_programs'
down_revision = 'add_meal_plans'
branch_labels = None
depends_on = None


def upgrade():
    """Create training_programs table."""
    op.create_table(
        'training_programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal', sa.String(length=100), nullable=False),
        sa.Column('experience_level', sa.String(length=50), nullable=False),
        sa.Column('days_per_week', sa.Integer(), nullable=False),
        sa.Column('equipment', JSON, nullable=True),
        sa.Column('program_data', JSON, nullable=False),
        sa.Column('summary', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_programs_id'), 'training_programs', ['id'], unique=False)
    op.create_index(op.f('ix_training_programs_user_id'), 'training_programs', ['user_id'], unique=False)


def downgrade():
    """Drop training_programs table."""
    op.drop_index(op.f('ix_training_programs_user_id'), table_name='training_programs')
    op.drop_index(op.f('ix_training_programs_id'), table_name='training_programs')
    op.drop_table('training_programs')
