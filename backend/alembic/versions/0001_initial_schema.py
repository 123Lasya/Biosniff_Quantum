"""Initial Bio-Sniff complete schema migration

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-12 08:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('FARMER', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. farmers table
    op.create_table(
        'farmers',
        sa.Column('farmer_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('profile_image', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('farmer_id')
    )
    op.create_index(op.f('ix_farmers_farmer_id'), 'farmers', ['farmer_id'], unique=False)
    op.create_index(op.f('ix_farmers_user_id'), 'farmers', ['user_id'], unique=True)
    op.create_index(op.f('ix_farmers_phone'), 'farmers', ['phone'], unique=False)
    op.create_index(op.f('ix_farmers_email'), 'farmers', ['email'], unique=False)

    # 3. farms table
    op.create_table(
        'farms',
        sa.Column('farm_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farmer_id', sa.Integer(), nullable=False),
        sa.Column('farm_name', sa.String(length=150), nullable=False),
        sa.Column('area', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('crop', sa.String(length=100), nullable=False, server_default='Rice (Paddy)'),
        sa.Column('crop_variety', sa.String(length=100), nullable=True),
        sa.Column('growth_stage', sa.String(length=100), nullable=True, server_default='Vegetative'),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('boundary_geojson', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.farmer_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('farm_id')
    )
    op.create_index(op.f('ix_farms_farm_id'), 'farms', ['farm_id'], unique=False)
    op.create_index(op.f('ix_farms_farmer_id'), 'farms', ['farmer_id'], unique=False)

    # 4. nodes table
    op.create_table(
        'nodes',
        sa.Column('node_id', sa.String(length=50), nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('node_name', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='online'),
        sa.Column('battery_percentage', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('signal_strength', sa.Float(), nullable=False, server_default='-65.0'),
        sa.Column('firmware_version', sa.String(length=50), nullable=False, server_default='v1.2.4-mesh'),
        sa.Column('is_master', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('node_id')
    )
    op.create_index(op.f('ix_nodes_node_id'), 'nodes', ['node_id'], unique=False)
    op.create_index(op.f('ix_nodes_farm_id'), 'nodes', ['farm_id'], unique=False)

    # 5. sensor_cycles table (Hourly cycle with exactly 10 gas readings + temp + hum + pressure)
    op.create_table(
        'sensor_cycles',
        sa.Column('cycle_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('cycle_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cycle_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('gas_readings', sa.JSON(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('humidity', sa.Float(), nullable=False),
        sa.Column('pressure', sa.Float(), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('raw_payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_id'], ['nodes.node_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('cycle_id')
    )
    op.create_index(op.f('ix_sensor_cycles_cycle_id'), 'sensor_cycles', ['cycle_id'], unique=False)
    op.create_index(op.f('ix_sensor_cycles_node_id'), 'sensor_cycles', ['node_id'], unique=False)
    op.create_index(op.f('ix_sensor_cycles_farm_id'), 'sensor_cycles', ['farm_id'], unique=False)
    op.create_index(op.f('ix_sensor_cycles_cycle_timestamp'), 'sensor_cycles', ['cycle_timestamp'], unique=False)

    # 6. predictions table (LSTM rolling 5-hour window)
    op.create_table(
        'predictions',
        sa.Column('prediction_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('cycle_id', sa.Integer(), nullable=False),
        sa.Column('window_cycle_ids', sa.JSON(), nullable=False),
        sa.Column('predicted_class', sa.String(length=100), nullable=False),
        sa.Column('disease_detected', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('anomaly_score', sa.Float(), nullable=True),
        sa.Column('raw_probabilities', sa.JSON(), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=False, server_default='lstm-rolling-5h-v1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cycle_id'], ['sensor_cycles.cycle_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_id'], ['nodes.node_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('prediction_id')
    )
    op.create_index(op.f('ix_predictions_prediction_id'), 'predictions', ['prediction_id'], unique=False)
    op.create_index(op.f('ix_predictions_node_id'), 'predictions', ['node_id'], unique=False)
    op.create_index(op.f('ix_predictions_farm_id'), 'predictions', ['farm_id'], unique=False)
    op.create_index(op.f('ix_predictions_disease_detected'), 'predictions', ['disease_detected'], unique=False)

    # 7. localization_results table
    op.create_table(
        'localization_results',
        sa.Column('localization_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('trigger_node_id', sa.String(length=50), nullable=False),
        sa.Column('trigger_prediction_id', sa.Integer(), nullable=True),
        sa.Column('estimated_latitude', sa.Float(), nullable=False),
        sa.Column('estimated_longitude', sa.Float(), nullable=False),
        sa.Column('confidence_radius_meters', sa.Float(), nullable=False, server_default='25.0'),
        sa.Column('affected_area_geojson', sa.JSON(), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trigger_node_id'], ['nodes.node_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trigger_prediction_id'], ['predictions.prediction_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('localization_id')
    )
    op.create_index(op.f('ix_localization_results_localization_id'), 'localization_results', ['localization_id'], unique=False)
    op.create_index(op.f('ix_localization_results_farm_id'), 'localization_results', ['farm_id'], unique=False)
    op.create_index(op.f('ix_localization_results_trigger_node_id'), 'localization_results', ['trigger_node_id'], unique=False)

    # 8. environment_readings table
    op.create_table(
        'environment_readings',
        sa.Column('reading_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=True),
        sa.Column('wind_speed', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('wind_direction', sa.String(length=20), nullable=True),
        sa.Column('soil_moisture', sa.Float(), nullable=True),
        sa.Column('ambient_temp', sa.Float(), nullable=False),
        sa.Column('humidity', sa.Float(), nullable=False),
        sa.Column('solar_radiation', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_id'], ['nodes.node_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('reading_id')
    )
    op.create_index(op.f('ix_environment_readings_reading_id'), 'environment_readings', ['reading_id'], unique=False)
    op.create_index(op.f('ix_environment_readings_farm_id'), 'environment_readings', ['farm_id'], unique=False)
    op.create_index(op.f('ix_environment_readings_recorded_at'), 'environment_readings', ['recorded_at'], unique=False)

    # 9. connectivity_logs table
    op.create_table(
        'connectivity_logs',
        sa.Column('log_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=True),
        sa.Column('gateway_type', sa.String(length=50), nullable=False, server_default='5G'),
        sa.Column('carrier', sa.String(length=50), nullable=False, server_default='Jio'),
        sa.Column('rssi', sa.Integer(), nullable=False, server_default='-78'),
        sa.Column('rsrp', sa.Integer(), nullable=True),
        sa.Column('rsrq', sa.Integer(), nullable=True),
        sa.Column('sinr', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=False, server_default='22.0'),
        sa.Column('packet_loss_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='connected'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_id'], ['nodes.node_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_connectivity_logs_log_id'), 'connectivity_logs', ['log_id'], unique=False)
    op.create_index(op.f('ix_connectivity_logs_farm_id'), 'connectivity_logs', ['farm_id'], unique=False)

    # 10. recommendations table
    op.create_table(
        'recommendations',
        sa.Column('recommendation_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('prediction_id', sa.Integer(), nullable=True),
        sa.Column('disease_name', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False, server_default='treatment'),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('dosage', sa.String(length=255), nullable=True),
        sa.Column('urgency', sa.String(length=50), nullable=False, server_default='immediate'),
        sa.Column('is_applied', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.prediction_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('recommendation_id')
    )
    op.create_index(op.f('ix_recommendations_recommendation_id'), 'recommendations', ['recommendation_id'], unique=False)
    op.create_index(op.f('ix_recommendations_farm_id'), 'recommendations', ['farm_id'], unique=False)

    # 11. alerts table
    op.create_table(
        'alerts',
        sa.Column('alert_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.String(length=50), nullable=True),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='warning'),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['node_id'], ['nodes.node_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('alert_id')
    )
    op.create_index(op.f('ix_alerts_alert_id'), 'alerts', ['alert_id'], unique=False)
    op.create_index(op.f('ix_alerts_farm_id'), 'alerts', ['farm_id'], unique=False)
    op.create_index(op.f('ix_alerts_alert_type'), 'alerts', ['alert_type'], unique=False)

    # 12. activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('activity_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('farm_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.farm_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('activity_id')
    )
    op.create_index(op.f('ix_activity_logs_activity_id'), 'activity_logs', ['activity_id'], unique=False)
    op.create_index(op.f('ix_activity_logs_user_id'), 'activity_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_activity_logs_farm_id'), 'activity_logs', ['farm_id'], unique=False)


def downgrade() -> None:
    op.drop_table('activity_logs')
    op.drop_table('alerts')
    op.drop_table('recommendations')
    op.drop_table('connectivity_logs')
    op.drop_table('environment_readings')
    op.drop_table('localization_results')
    op.drop_table('predictions')
    op.drop_table('sensor_cycles')
    op.drop_table('nodes')
    op.drop_table('farms')
    op.drop_table('farmers')
    op.drop_table('users')
