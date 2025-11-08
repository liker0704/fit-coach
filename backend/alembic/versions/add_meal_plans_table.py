"""add meal plans table

Revision ID: add_meal_plans
Revises: add_audit_logs
Create Date: 2025-11-08 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = 'add_meal_plans'
down_revision = 'add_audit_logs'
branch_labels = None
depends_on = None


def upgrade():
    """Create meal_plans table."""
    op.create_table(
        'meal_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('calorie_target', sa.Integer(), nullable=False),
        sa.Column('dietary_preferences', JSON, nullable=True),
        sa.Column('allergies', JSON, nullable=True),
        sa.Column('plan_data', JSON, nullable=False),
        sa.Column('summary', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_meal_plans_id'), 'meal_plans', ['id'], unique=False)
    op.create_index(op.f('ix_meal_plans_user_id'), 'meal_plans', ['user_id'], unique=False)


def downgrade():
    """Drop meal_plans table."""
    op.drop_index(op.f('ix_meal_plans_user_id'), table_name='meal_plans')
    op.drop_index(op.f('ix_meal_plans_id'), table_name='meal_plans')
    op.drop_table('meal_plans')
