"""add timestamp, window_start, window_end, all_class_probabilities to predictions

Revision ID: 0003_prediction_window_timestamps
Revises: 0002_sensor_cycle_battery_signal
Create Date: 2026-09-12 08:37:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_prediction_window_timestamps'
down_revision: Union[str, None] = '0002_sensor_cycle_battery_signal'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('predictions', sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True))
    op.add_column('predictions', sa.Column('window_start', sa.DateTime(timezone=True), nullable=True))
    op.add_column('predictions', sa.Column('window_end', sa.DateTime(timezone=True), nullable=True))
    op.add_column('predictions', sa.Column('all_class_probabilities', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('predictions', 'all_class_probabilities')
    op.drop_column('predictions', 'window_end')
    op.drop_column('predictions', 'window_start')
    op.drop_column('predictions', 'timestamp')
