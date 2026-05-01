"""add wechat_openid to users and guest_id to screenings

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-05-01 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3e4f5a6b7c8'
down_revision = 'c2d3e4f5a6b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add wechat_openid to users table
    op.add_column(
        'users',
        sa.Column('wechat_openid', sa.String(64), nullable=True)
    )
    op.create_unique_constraint('uq_users_wechat_openid', 'users', ['wechat_openid'])
    op.create_index('ix_users_wechat_openid', 'users', ['wechat_openid'], unique=True)

    # Add guest_id to screenings table
    op.add_column(
        'screenings',
        sa.Column('guest_id', sa.String(64), nullable=True)
    )
    op.create_index('ix_screenings_guest_id', 'screenings', ['guest_id'], unique=False)


def downgrade() -> None:
    # Remove guest_id from screenings
    op.drop_index('ix_screenings_guest_id', table_name='screenings')
    op.drop_column('screenings', 'guest_id')

    # Remove wechat_openid from users
    op.drop_index('ix_users_wechat_openid', table_name='users')
    op.drop_constraint('uq_users_wechat_openid', 'users', type_='unique')
    op.drop_column('users', 'wechat_openid')
