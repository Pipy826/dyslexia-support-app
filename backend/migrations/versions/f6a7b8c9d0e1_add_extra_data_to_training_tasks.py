"""add extra_data to training_tasks

Revision ID: f6a7b8c9d0e1
Revises: e4f5a6b7c8d9
Create Date: 2026-06-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = 'e4f5a6b7c8d9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'training_tasks',
        sa.Column('extra_data', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('training_tasks', 'extra_data')
