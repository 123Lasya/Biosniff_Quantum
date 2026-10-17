"""add predicted source x, y, source_score, trigger_nodes, detected_conditions, affected_zone to localization_results

Revision ID: 0004_localization_source_estimation
Revises: 0003_prediction_window_timestamps
Create Date: 2026-09-12 01:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0004_localization_source_estimation'
down_revision: Union[str, None] = '0003_prediction_window_timestamps'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('localization_results', schema=None) as batch_op:
        batch_op.add_column(sa.Column('predicted_source_x', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('predicted_source_y', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('source_score', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('trigger_nodes', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('detected_conditions', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('affected_zone', sa.JSON(), nullable=True))
        batch_op.alter_column('trigger_node_id', existing_type=sa.String(length=50), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('localization_results', schema=None) as batch_op:
        batch_op.drop_column('affected_zone')
        batch_op.drop_column('detected_conditions')
        batch_op.drop_column('trigger_nodes')
        batch_op.drop_column('source_score')
        batch_op.drop_column('predicted_source_y')
        batch_op.drop_column('predicted_source_x')
        batch_op.alter_column('trigger_node_id', existing_type=sa.String(length=50), nullable=False)
