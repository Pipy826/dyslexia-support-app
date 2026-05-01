"""add streak fields to children

Revision ID: b1c2d3e4f5a6
Revises: 482aa99fdbea
Create Date: 2026-04-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c2d3e4f5a6'
down_revision = '482aa99fdbea'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 为 children 表添加连续打卡字段
    op.add_column('children', sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('children', sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('children', sa.Column('last_activity_date', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('children', 'last_activity_date')
    op.drop_column('children', 'longest_streak')
    op.drop_column('children', 'current_streak')
