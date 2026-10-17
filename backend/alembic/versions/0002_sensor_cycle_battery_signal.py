"""add battery and signal to sensor_cycles and pressure to environment_readings

Revision ID: 0002_sensor_cycle_battery_signal
Revises: 0001_initial_schema
Create Date: 2026-09-12 08:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_sensor_cycle_battery_signal'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add battery and signal to sensor_cycles
    op.add_column('sensor_cycles', sa.Column('battery', sa.Float(), nullable=True))
    op.add_column('sensor_cycles', sa.Column('signal', sa.Float(), nullable=True))
    # Add pressure to environment_readings
    op.add_column('environment_readings', sa.Column('pressure', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('environment_readings', 'pressure')
    op.drop_column('sensor_cycles', 'signal')
    op.drop_column('sensor_cycles', 'battery')
