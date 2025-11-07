"""add_agent_system_tables

Revision ID: 4232ee534200
Revises: 2153c821205e
Create Date: 2025-11-02 22:11:03.034617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4232ee534200'
down_revision: Union[str, None] = '2153c821205e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create agent_memories table
    op.create_table(
        'agent_memories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('memory_type', sa.String(length=20), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_agent_memories_user_agent', 'agent_memories', ['user_id', 'agent_type'])
    op.create_index('idx_agent_memories_type', 'agent_memories', ['memory_type'])

    # Create agent_conversations table
    op.create_table(
        'agent_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_agent_conversations_user_session', 'agent_conversations', ['user_id', 'session_id'])
    op.create_index('idx_agent_conversations_created', 'agent_conversations', [sa.text('created_at DESC')])

    # Create agent_costs table
    op.create_table(
        'agent_costs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False),
        sa.Column('tokens_input', sa.Integer(), nullable=False),
        sa.Column('tokens_output', sa.Integer(), nullable=False),
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_agent_costs_user_created', 'agent_costs', ['user_id', sa.text('created_at DESC')])

    # Add photo processing fields to meals table
    op.add_column('meals', sa.Column('photo_path', sa.String(length=500), nullable=True))
    op.add_column('meals', sa.Column('photo_processing_status', sa.String(length=20), server_default='pending', nullable=True))
    op.add_column('meals', sa.Column('photo_processing_error', sa.Text(), nullable=True))
    op.add_column('meals', sa.Column('ai_recognized_items', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove photo processing fields from meals table
    op.drop_column('meals', 'ai_recognized_items')
    op.drop_column('meals', 'photo_processing_error')
    op.drop_column('meals', 'photo_processing_status')
    op.drop_column('meals', 'photo_path')

    # Drop agent_costs table
    op.drop_index('idx_agent_costs_user_created', table_name='agent_costs')
    op.drop_table('agent_costs')

    # Drop agent_conversations table
    op.drop_index('idx_agent_conversations_created', table_name='agent_conversations')
    op.drop_index('idx_agent_conversations_user_session', table_name='agent_conversations')
    op.drop_table('agent_conversations')

    # Drop agent_memories table
    op.drop_index('idx_agent_memories_type', table_name='agent_memories')
    op.drop_index('idx_agent_memories_user_agent', table_name='agent_memories')
    op.drop_table('agent_memories')
