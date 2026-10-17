#!/usr/bin/env python3
"""
BIO-SNIFF IoT System - Comprehensive Demo Data Seeding Script
============================================================
Idempotent script to populate development and testing environments with:
- Admin user (admin@biosniff.gov.in)
- Farmer user (ramesh.patil@biosniff.com) and additional regional farmers
- Farms with geographic boundaries across Indian states
- Up to 3 sensor nodes per farm with GPS coordinates
- 24-hour cycle history with valid 10 gas-resistance readings
- ML predictions (Attention Bi-LSTM)
- Spatial localization results with affected zones
- Agronomic recommendations & alerts
- Environment & 5G connectivity logs

Usage:
  python3 scripts/seed_demo_data.py
  (or: python3 backend/scripts/seed_demo_data.py)
"""

import sys
import os
import json
import math
from datetime import datetime, timezone, timedelta

# Ensure backend root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend") if os.path.exists(os.path.join(PROJECT_ROOT, "backend")) else PROJECT_ROOT

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.node import Node
from app.models.sensor_cycle import SensorCycle
from app.models.prediction import Prediction
from app.models.localization import LocalizationResult
from app.models.recommendation import Recommendation
from app.models.alert import Alert
from app.models.environment import EnvironmentReading
from app.models.connectivity import ConnectivityLog
from app.models.activity import ActivityLog


def seed_data():
    print("=" * 60)
    print("BIO-SNIFF: Initializing Idempotent Demo Data Seed...")
    print("=" * 60)

    # Note: Alembic manages schema, but ensure tables exist if running on empty test database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    now = datetime.now(timezone.utc)

    try:
        # 1. ADMIN USER
        admin_email = "admin@biosniff.gov.in"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email=admin_email,
                hashed_password=get_password_hash("Admin@123456"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.flush()
            print(f" [+] Created Admin: {admin_email} / Admin@123456")
        else:
            print(f" [=] Admin already exists: {admin_email}")

        # 2. FARMERS
        farmers_data = [
            {
                "username": "ramesh_patil",
                "email": "ramesh.patil@biosniff.com",
                "password": "Farmer@123456",
                "name": "Ramesh Patil",
                "phone": "+91 98220 12345",
                "state": "Maharashtra",
                "district": "Ahmednagar",
                "address": "Plot 42, Rahuri, Ahmednagar",
                "farm": {
                    "name": "Patil Organic Paddy Farm",
                    "crop": "Rice",
                    "crop_variety": "Basmati 1121",
                    "stage": "Tillering",
                    "area": 4.6,
                    "lat": 19.3919,
                    "lng": 74.6528,
                    "status": "active"
                }
            },
            {
                "username": "suresh_singh",
                "email": "suresh.singh@biosniff.com",
                "password": "Farmer@123456",
                "name": "Suresh Singh",
                "phone": "+91 98140 54321",
                "state": "Punjab",
                "district": "Ludhiana",
                "address": "Village Sahnewal, Ludhiana",
                "farm": {
                    "name": "Singh Golden Wheat Estate",
                    "crop": "Wheat",
                    "crop_variety": "HD-3086",
                    "stage": "Crown Root",
                    "area": 8.2,
                    "lat": 30.9010,
                    "lng": 75.8573,
                    "status": "active"
                }
            },
            {
                "username": "ananya_sen",
                "email": "ananya.sen@biosniff.com",
                "password": "Farmer@123456",
                "name": "Ananya Sen",
                "phone": "+91 94330 98765",
                "state": "West Bengal",
                "district": "Burdwan",
                "address": "Galsi Block, Purba Bardhaman",
                "farm": {
                    "name": "Burdwan High-Yield Rice Fields",
                    "crop": "Rice",
                    "crop_variety": "Swarna (MTU 7029)",
                    "stage": "Panicle Initiation",
                    "area": 6.5,
                    "lat": 23.2324,
                    "lng": 87.8615,
                    "status": "active"
                }
            },
            {
                "username": "venkatesh_rao",
                "email": "venkatesh.rao@biosniff.com",
                "password": "Farmer@123456",
                "name": "Venkatesh Rao",
                "phone": "+91 98480 33445",
                "state": "Andhra Pradesh",
                "district": "Guntur",
                "address": "Tenali Road, Guntur Rural",
                "farm": {
                    "name": "Krishna Delta Chili & Cotton",
                    "crop": "Cotton",
                    "crop_variety": "Bt Cotton RCH-2",
                    "stage": "Square Formation",
                    "area": 5.1,
                    "lat": 16.3067,
                    "lng": 80.4365,
                    "status": "active"
                }
            }
        ]

        primary_farm = None

        for fd in farmers_data:
            user = db.query(User).filter(User.email == fd["email"]).first()
            if not user:
                user = User(
                    username=fd["username"],
                    email=fd["email"],
                    hashed_password=get_password_hash(fd["password"]),
                    role=UserRole.FARMER,
                    is_active=True
                )
                db.add(user)
                db.flush()

            farmer = db.query(Farmer).filter(Farmer.user_id == user.user_id).first()
            if not farmer:
                farmer = Farmer(
                    user_id=user.user_id,
                    full_name=fd["name"],
                    phone=fd["phone"],
                    email=fd["email"],
                    address=fd["address"],
                    state=fd["state"],
                    district=fd["district"]
                )
                db.add(farmer)
                db.flush()
                print(f" [+] Created Farmer: {fd['name']} ({fd['email']})")

            # Farm
            f_spec = fd["farm"]
            farm = db.query(Farm).filter(Farm.farmer_id == farmer.farmer_id, Farm.farm_name == f_spec["name"]).first()
            if not farm:
                # Boundary box around coordinates
                lat, lng = f_spec["lat"], f_spec["lng"]
                boundary_coords = [
                    {"lat": round(lat + 0.0015, 6), "lng": round(lng - 0.0012, 6)},
                    {"lat": round(lat + 0.0012, 6), "lng": round(lng + 0.0016, 6)},
                    {"lat": round(lat - 0.0012, 6), "lng": round(lng + 0.0013, 6)},
                    {"lat": round(lat - 0.0008, 6), "lng": round(lng - 0.0016, 6)},
                    {"lat": round(lat + 0.0015, 6), "lng": round(lng - 0.0012, 6)}
                ]
                farm = Farm(
                    farmer_id=farmer.farmer_id,
                    farm_name=f_spec["name"],
                    crop=f_spec["crop"],
                    crop_variety=f_spec["crop_variety"],
                    growth_stage=f_spec["stage"],
                    area=f_spec["area"],
                    latitude=f_spec["lat"],
                    longitude=f_spec["lng"],
                    address=farmer.address,
                    boundary_geojson=json.dumps(boundary_coords),
                    status=f_spec["status"]
                )
                db.add(farm)
                db.flush()
                print(f" [+] Created Farm: {f_spec['name']} in {farmer.state}")

            if fd["email"] == "ramesh.patil@biosniff.com":
                primary_farm = farm

        db.commit()

        # 3. NODES FOR PRIMARY FARM
        if primary_farm:
            nodes_data = [
                {
                    "node_id": "NODE_01",
                    "name": "Node 1 - North Canopy",
                    "lat": 19.3925,
                    "lng": 74.6532,
                    "battery": 92.0,
                    "signal": -72.0,
                    "is_master": True,
                    "firmware": "v2.3.1"
                },
                {
                    "node_id": "NODE_02",
                    "name": "Node 2 - South Boundary",
                    "lat": 19.3912,
                    "lng": 74.6521,
                    "battery": 88.0,
                    "signal": -78.0,
                    "is_master": False,
                    "firmware": "v2.3.1"
                },
                {
                    "node_id": "NODE_03",
                    "name": "Node 3 - East Trench",
                    "lat": 19.3918,
                    "lng": 74.6539,
                    "battery": 95.0,
                    "signal": -69.0,
                    "is_master": False,
                    "firmware": "v2.3.1"
                }
            ]

            for nd in nodes_data:
                node = db.query(Node).filter(Node.node_id == nd["node_id"]).first()
                if not node:
                    node = Node(
                        node_id=nd["node_id"],
                        farm_id=primary_farm.farm_id,
                        node_name=nd["name"],
                        latitude=nd["lat"],
                        longitude=nd["lng"],
                        battery_percentage=nd["battery"],
                        signal_strength=nd["signal"],
                        is_master=nd["is_master"],
                        firmware_version=nd["firmware"],
                        status="online",
                        last_seen=now
                    )
                    db.add(node)
                    print(f" [+] Created Node: {nd['node_id']} ({nd['name']})")
                else:
                    node.farm_id = primary_farm.farm_id
                    node.battery_percentage = nd["battery"]
                    node.signal_strength = nd["signal"]
                    node.status = "online"
                    node.last_seen = now

            db.commit()

            # 4. SENSOR CYCLES (24 Hours History)
            existing_cycles = db.query(SensorCycle).filter(SensorCycle.farm_id == primary_farm.farm_id).count()
            if existing_cycles < 24:
                print(" [+] Populating 24-hour cycle history for 3 nodes...")
                for h in range(24, 0, -1):
                    cycle_time = now - timedelta(hours=h)
                    diurnal_factor = math.sin((h / 24.0) * 2 * math.pi)

                    # Node 1: Slightly elevated VOC (affected by disease)
                    db.add(SensorCycle(
                        node_id="NODE_01",
                        farm_id=primary_farm.farm_id,
                        cycle_timestamp=cycle_time,
                        cycle_number=25 - h,
                        gas_readings=[
                            round(145.0 - h * 1.2 + (i * 2.5), 1) for i in range(10)
                        ],
                        temperature=round(27.5 + diurnal_factor * 4.0, 1),
                        humidity=round(74.0 - diurnal_factor * 12.0, 1),
                        pressure=round(1008.2 + (h % 3) * 0.4, 1),
                        battery=round(92.0 - (24 - h) * 0.1, 1),
                        signal=round(-72.0 + (h % 2), 1),
                        is_valid=True
                    ))

                    # Node 2: Healthy baseline
                    db.add(SensorCycle(
                        node_id="NODE_02",
                        farm_id=primary_farm.farm_id,
                        cycle_timestamp=cycle_time,
                        cycle_number=25 - h,
                        gas_readings=[
                            round(220.0 - (i * 1.8), 1) for i in range(10)
                        ],
                        temperature=round(27.1 + diurnal_factor * 3.8, 1),
                        humidity=round(75.5 - diurnal_factor * 11.5, 1),
                        pressure=round(1008.5 + (h % 3) * 0.4, 1),
                        battery=round(88.0 - (24 - h) * 0.1, 1),
                        signal=round(-78.0 + (h % 3), 1),
                        is_valid=True
                    ))

                    # Node 3: Moderate VOC elevation
                    db.add(SensorCycle(
                        node_id="NODE_03",
                        farm_id=primary_farm.farm_id,
                        cycle_timestamp=cycle_time,
                        cycle_number=25 - h,
                        gas_readings=[
                            round(160.0 - h * 0.8 + (i * 2.1), 1) for i in range(10)
                        ],
                        temperature=round(27.8 + diurnal_factor * 4.1, 1),
                        humidity=round(73.2 - diurnal_factor * 12.2, 1),
                        pressure=round(1008.0 + (h % 3) * 0.4, 1),
                        battery=round(95.0 - (24 - h) * 0.1, 1),
                        signal=round(-69.0 + (h % 2), 1),
                        is_valid=True
                    ))

                db.commit()

            # 5. PREDICTIONS
            latest_c1 = db.query(SensorCycle).filter(SensorCycle.node_id == "NODE_01").order_by(SensorCycle.cycle_timestamp.desc()).first()
            latest_c2 = db.query(SensorCycle).filter(SensorCycle.node_id == "NODE_02").order_by(SensorCycle.cycle_timestamp.desc()).first()
            latest_c3 = db.query(SensorCycle).filter(SensorCycle.node_id == "NODE_03").order_by(SensorCycle.cycle_timestamp.desc()).first()

            existing_preds = db.query(Prediction).filter(Prediction.farm_id == primary_farm.farm_id).count()
            if existing_preds == 0:
                print(" [+] Seeding rolling ML inference predictions...")
                window_start = now - timedelta(hours=5)
                window_end = now

                # Node 1: Rice Blast (Confidence 94.2%)
                c1_id = latest_c1.cycle_id if latest_c1 else 1
                db.add(Prediction(
                    node_id="NODE_01",
                    farm_id=primary_farm.farm_id,
                    cycle_id=c1_id,
                    window_cycle_ids=[max(1, c1_id - 4), max(1, c1_id - 3), max(1, c1_id - 2), max(1, c1_id - 1), c1_id],
                    timestamp=now,
                    window_start=window_start,
                    window_end=window_end,
                    predicted_class="Rice_Blast",
                    disease_detected=True,
                    confidence=0.942,
                    anomaly_score=0.12,
                    all_class_probabilities={
                        "Rice_Blast": 0.942,
                        "Rice_Bacterial_Blight": 0.024,
                        "Rice_Brown_Spot": 0.018,
                        "Rice_Healthy": 0.016,
                        "Rice_Sheath_Blight": 0.0
                    },
                    model_version="BiLSTM-Attn-v2.1"
                ))

                # Node 2: Healthy (Confidence 96.1%)
                c2_id = latest_c2.cycle_id if latest_c2 else 2
                db.add(Prediction(
                    node_id="NODE_02",
                    farm_id=primary_farm.farm_id,
                    cycle_id=c2_id,
                    window_cycle_ids=[max(1, c2_id - 4), max(1, c2_id - 3), max(1, c2_id - 2), max(1, c2_id - 1), c2_id],
                    timestamp=now,
                    window_start=window_start,
                    window_end=window_end,
                    predicted_class="Rice_Healthy",
                    disease_detected=False,
                    confidence=0.961,
                    anomaly_score=0.04,
                    all_class_probabilities={
                        "Rice_Blast": 0.012,
                        "Rice_Bacterial_Blight": 0.008,
                        "Rice_Brown_Spot": 0.011,
                        "Rice_Healthy": 0.961,
                        "Rice_Sheath_Blight": 0.008
                    },
                    model_version="BiLSTM-Attn-v2.1"
                ))

                # Node 3: Rice Blast early signs (Confidence 89.5%)
                c3_id = latest_c3.cycle_id if latest_c3 else 3
                db.add(Prediction(
                    node_id="NODE_03",
                    farm_id=primary_farm.farm_id,
                    cycle_id=c3_id,
                    window_cycle_ids=[max(1, c3_id - 4), max(1, c3_id - 3), max(1, c3_id - 2), max(1, c3_id - 1), c3_id],
                    timestamp=now,
                    window_start=window_start,
                    window_end=window_end,
                    predicted_class="Rice_Blast",
                    disease_detected=True,
                    confidence=0.895,
                    anomaly_score=0.15,
                    all_class_probabilities={
                        "Rice_Blast": 0.895,
                        "Rice_Bacterial_Blight": 0.045,
                        "Rice_Brown_Spot": 0.030,
                        "Rice_Healthy": 0.030,
                        "Rice_Sheath_Blight": 0.0
                    },
                    model_version="BiLSTM-Attn-v2.1"
                ))
                db.commit()

            # 6. LOCALIZATION RESULT
            existing_loc = db.query(LocalizationResult).filter(LocalizationResult.farm_id == primary_farm.farm_id).first()
            if not existing_loc:
                print(" [+] Seeding wind-aware disease localization result...")
                db.add(LocalizationResult(
                    farm_id=primary_farm.farm_id,
                    trigger_node_id="NODE_01",
                    estimated_latitude=19.3923,
                    estimated_longitude=74.6534,
                    predicted_source_x=42.5,
                    predicted_source_y=88.2,
                    source_score=0.942,
                    confidence_radius_meters=14.5,
                    trigger_nodes=["NODE_01", "NODE_03"],
                    detected_conditions=["Rice_Blast"],
                    affected_zone={
                        "name": "North-East Sector",
                        "center": {"lat": 19.3923, "lng": 74.6534},
                        "radius_m": 14.5,
                        "severity": "critical"
                    },
                    status="active",
                    severity="critical"
                ))
                db.commit()

            # 7. RECOMMENDATIONS
            existing_rec = db.query(Recommendation).filter(Recommendation.farm_id == primary_farm.farm_id).first()
            if not existing_rec:
                print(" [+] Seeding agronomic disease recommendations...")
                db.add(Recommendation(
                    farm_id=primary_farm.farm_id,
                    disease_name="Rice_Blast",
                    title="Apply Tricyclazole 75% WP",
                    action_type="fungicide_treatment",
                    details="Foliar spray of Tricyclazole 75% WP @ 0.6 g/L water across the North-East canopy zone within 24 hours to prevent conidial dispersion.",
                    dosage="0.6 g/L water (120 g/acre)",
                    urgency="immediate",
                    is_applied=False
                ))
                db.commit()

            # 8. ALERTS
            existing_alerts = db.query(Alert).filter(Alert.farm_id == primary_farm.farm_id).count()
            if existing_alerts == 0:
                print(" [+] Seeding system and disease alerts...")
                alerts_to_add = [
                    Alert(
                        farm_id=primary_farm.farm_id,
                        node_id="NODE_01",
                        alert_type="disease_detected",
                        severity="critical",
                        title="Rice Blast Detected in North-East Sector",
                        message="Attention Bi-LSTM model confirmed Rice Blast at Node 1 (confidence 94.2%). Localized to North-East sector.",
                        is_read=False,
                        is_acknowledged=False,
                        created_at=now - timedelta(minutes=35)
                    ),
                    Alert(
                        farm_id=primary_farm.farm_id,
                        node_id=None,
                        alert_type="connectivity",
                        severity="info",
                        title="5G NSA Gateway Connected",
                        message="Master Gateway connected on Jio 5G with stable 18ms latency.",
                        is_read=True,
                        is_acknowledged=True,
                        created_at=now - timedelta(hours=3)
                    ),
                    Alert(
                        farm_id=primary_farm.farm_id,
                        node_id="NODE_02",
                        alert_type="battery_health",
                        severity="info",
                        title="Node 2 Battery Optimal",
                        message="Node 2 battery level healthy at 88% with solar trickle charging.",
                        is_read=True,
                        is_acknowledged=True,
                        created_at=now - timedelta(hours=6)
                    )
                ]
                db.add_all(alerts_to_add)
                db.commit()

            # 9. ENVIRONMENT READINGS & CONNECTIVITY LOGS
            existing_env = db.query(EnvironmentReading).filter(EnvironmentReading.farm_id == primary_farm.farm_id).count()
            if existing_env < 24:
                print(" [+] Seeding 24-hour environment & 5G connectivity time-series...")
                for h in range(24, 0, -1):
                    rec_time = now - timedelta(hours=h)
                    diurnal = math.sin((h / 24.0) * 2 * math.pi)

                    db.add(EnvironmentReading(
                        farm_id=primary_farm.farm_id,
                        node_id="NODE_01",
                        wind_speed=round(2.2 + abs(diurnal) * 1.5, 1),
                        wind_direction="NE (48°)",
                        soil_moisture=round(72.0 - diurnal * 4.0, 1),
                        ambient_temp=round(28.0 + diurnal * 4.2, 1),
                        humidity=round(72.0 - diurnal * 12.0, 1),
                        pressure=1008.2,
                        solar_radiation=round(520.0 + max(0.0, diurnal) * 350.0, 1),
                        recorded_at=rec_time
                    ))

                    db.add(ConnectivityLog(
                        farm_id=primary_farm.farm_id,
                        node_id="NODE_01",
                        gateway_type="5G",
                        carrier="Jio",
                        rssi=-78 + (h % 3),
                        rsrp=-88,
                        rsrq=-11,
                        sinr=16,
                        latency_ms=18.0 + (h % 3),
                        packet_loss_pct=1.2,
                        status="connected",
                        recorded_at=rec_time
                    ))

                db.commit()

            # 10. ACTIVITY LOGS
            existing_acts = db.query(ActivityLog).filter(ActivityLog.farm_id == primary_farm.farm_id).count()
            if existing_acts == 0:
                print(" [+] Seeding activity logs...")
                db.add_all([
                    ActivityLog(
                        user_id=admin_user.user_id,
                        farm_id=primary_farm.farm_id,
                        action="system_ingest",
                        details={"message": "Hourly cycle #24 received from Master Gateway NODE_01"},
                        created_at=now - timedelta(minutes=15)
                    ),
                    ActivityLog(
                        user_id=admin_user.user_id,
                        farm_id=primary_farm.farm_id,
                        action="ml_inference",
                        details={"message": "Bi-LSTM Attention inference completed: Rice_Blast (94.2% confidence)"},
                        created_at=now - timedelta(minutes=14)
                    ),
                    ActivityLog(
                        user_id=admin_user.user_id,
                        farm_id=primary_farm.farm_id,
                        action="spatial_localization",
                        details={"message": "Localization estimated source centroid at (19.3923, 74.6534), radius 14.5m"},
                        created_at=now - timedelta(minutes=13)
                    )
                ])
                db.commit()

        print("=" * 60)
        print("BIO-SNIFF: Demo data seeding completed successfully!")
        print("  - Admin:   admin@biosniff.gov.in / Admin@123456")
        print("  - Farmer:  ramesh.patil@biosniff.com / Farmer@123456")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"[!] Error seeding data: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
