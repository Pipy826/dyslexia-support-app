"""add ai_notifications table

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-05-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4f5a6b7c8d9'
down_revision = 'd3e4f5a6b7c8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ai_notifications',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('child_id', sa.Integer(), sa.ForeignKey('children.id'), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('game_type', sa.String(50), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('ai_notifications')
