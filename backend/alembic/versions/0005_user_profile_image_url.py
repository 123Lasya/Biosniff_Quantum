"""Add profile_image_url to users table

Revision ID: 0005_user_profile_image_url
Revises: 0004_localization_source_estimation
Create Date: 2026-09-17 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0005_user_profile_image_url'
down_revision: Union[str, None] = '0004_localization_source_estimation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    try:
        op.add_column('users', sa.Column('profile_image_url', sa.String(length=500), nullable=True))
    except Exception:
        pass


def downgrade() -> None:
    try:
        op.drop_column('users', 'profile_image_url')
    except Exception:
        pass
