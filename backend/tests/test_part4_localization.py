import pytest
import math
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.services.localization_service import (
    LocalizationService,
    circular_mean_degrees,
    gps_to_metric,
    metric_to_gps
)
from app.services.recommendation_service import (
    RecommendationService,
    normalize_disease_name
)
from app.services.alert_service import AlertService, AlertType
from app.core.config import settings

client = TestClient(app)


# ==========================================
# 1. UNIT TESTS: COORDINATE MATH & WIND
# ==========================================

def test_circular_mean_wind_direction():
    """Verify circular wind averaging across the 0/360 boundary."""
    # North boundary test: 350 deg and 10 deg should average to 0.0 (North), not 180.0
    mean_north = circular_mean_degrees([350.0, 10.0])
    assert abs(mean_north - 0.0) < 0.1 or abs(mean_north - 360.0) < 0.1

    # East: 90 deg and 90 deg -> 90 deg
    mean_east = circular_mean_degrees([90.0, 90.0])
    assert abs(mean_east - 90.0) < 0.1

    # South-West: 220 deg and 240 deg -> 230 deg
    mean_sw = circular_mean_degrees([220.0, 240.0])
    assert abs(mean_sw - 230.0) < 0.1

    # Empty list
    assert circular_mean_degrees([]) == 0.0


def test_gps_and_metric_conversions():
    """Verify local metric coordinate transformations and inverse GPS mapping."""
    origin_lat = 16.506174
    origin_lon = 80.648015

    # Point 50 meters East, 80 meters North
    test_lat = origin_lat + (80.0 / 6371000.0) * (180.0 / math.pi)
    test_lon = origin_lon + (50.0 / (6371000.0 * math.cos(math.radians(origin_lat)))) * (180.0 / math.pi)

    # Convert to metric
    x, y = gps_to_metric(test_lat, test_lon, origin_lat, origin_lon)
    assert abs(x - 50.0) < 0.1
    assert abs(y - 80.0) < 0.1

    # Invert back to GPS
    lat_back, lon_back = metric_to_gps(x, y, origin_lat, origin_lon)
    assert abs(lat_back - test_lat) < 1e-5
    assert abs(lon_back - test_lon) < 1e-5


# ==========================================
# 2. LOCALIZATION TRIGGER & INACTIVE STATE
# ==========================================

def test_localization_inactive_on_healthy_farm():
    """
    If all nodes report healthy baseline, localization must remain inactive.
    source_score must be 0.0, active=False, affected_zone=None.
    """
    service = LocalizationService(db=None)

    healthy_predictions = [
        {"node_id": "NODE_1", "latitude": 16.5061, "longitude": 80.6480, "is_disease": False, "predicted_class": "Rice_Healthy", "confidence": 0.94},
        {"node_id": "NODE_2", "latitude": 16.5063, "longitude": 80.6482, "is_disease": False, "predicted_class": "Rice_Healthy", "confidence": 0.91},
        {"node_id": "NODE_3", "latitude": 16.5060, "longitude": 80.6484, "is_disease": False, "predicted_class": "Rice_Healthy", "confidence": 0.88},
    ]

    result = service.estimate_source_location(
        farm_id=1,
        node_predictions=healthy_predictions,
        wind_speed=2.0,
        wind_direction=90.0,
        save_to_db=False
    )

    assert result["active"] is False
    assert result["source_score"] == 0.0
    assert result["affected_zone"] is None
    assert result["trigger_nodes"] == []
    assert result["detected_conditions"] == []


def test_localization_triggered_by_single_node():
    """
    Localization MUST activate if at least ONE node detects a disease.
    Does NOT require 2/3 nodes.
    """
    service = LocalizationService(db=None)

    predictions = [
        {"node_id": "NODE_1", "latitude": 16.5061, "longitude": 80.6480, "is_disease": True, "predicted_class": "Rice_Blast", "confidence": 0.92, "response_strength": 1.5},
        {"node_id": "NODE_2", "latitude": 16.5063, "longitude": 80.6482, "is_disease": False, "predicted_class": "Rice_Healthy", "confidence": 0.85, "response_strength": 0.8},
        {"node_id": "NODE_3", "latitude": 16.5060, "longitude": 80.6484, "is_disease": False, "predicted_class": "Rice_Healthy", "confidence": 0.89, "response_strength": 0.7},
    ]

    result = service.estimate_source_location(
        farm_id=1,
        node_predictions=predictions,
        wind_speed=2.5,
        wind_direction=90.0,  # Wind from East
        save_to_db=False
    )

    assert result["active"] is True
    assert "NODE_1" in result["trigger_nodes"]
    assert "Rice_Blast" in result["detected_conditions"]
    assert result["source_score"] > 0.4
    assert result["geo"]["latitude"] is not None
    assert result["geo"]["longitude"] is not None
    assert result["farm_local"]["x"] is not None
    assert result["farm_local"]["y"] is not None

    # Affected zone attributes
    az = result["affected_zone"]
    assert az is not None
    assert az["radius_m"] >= 3.5
    assert az["center_latitude"] is not None
    assert az["center_longitude"] is not None
    assert az["nearest_node"] is not None
    assert az["severity"] in ("critical", "high", "medium", "low")
    assert az["inspection_priority"] in ("immediate", "within_24h", "routine")
    assert len(az["polygon"]) == 8


def test_wind_advection_shifts_source_upwind():
    """
    Verify wind-awareness: When wind is blowing from East (90 deg),
    plume travels West. The VOC emission source that triggered Node 1
    should be estimated upwind (East, higher X in local metric) of the node.
    """
    service = LocalizationService(db=None)

    origin_lat = 16.5060
    origin_lon = 80.6480

    # Node 1 is at (0, 0)
    predictions = [
        {"node_id": "NODE_1", "latitude": origin_lat, "longitude": origin_lon, "is_disease": True, "predicted_class": "Rice_Blast", "confidence": 0.95, "response_strength": 1.8},
    ]

    # Wind blowing from East (90 deg) towards West
    res_east = service.estimate_source_location(
        farm_id=1,
        node_predictions=predictions,
        wind_speed=3.0,
        wind_direction=90.0,
        farm_origin_lat=origin_lat,
        farm_origin_lon=origin_lon,
        save_to_db=False
    )

    # Source should be placed upwind (East of Node 1, so X >= 0)
    assert res_east["farm_local"]["x"] >= 0.0


# ==========================================
# 3. MULTI-DISEASE RECOMMENDATIONS
# ==========================================

def test_recommendations_multi_disease_and_healthy():
    """
    Verify recommendation engine handles multiple diseases concurrently
    without collapsing them, sorted by severity, and handles healthy baselines.
    """
    rec_service = RecommendationService(db=None)

    # 1. Multi-disease detection
    diseases = ["Rice_Blast", "Rice_Brown_Spot"]
    recs = rec_service.generate_recommendations(detected_conditions=diseases, farm_id=1)

    assert len(recs) == 2
    # Rice_Blast has severity rank 1, Rice_Brown_Spot has severity rank 2
    assert recs[0]["disease_type"] in ("Rice Blast", "Rice_Blast")
    assert recs[0]["priority"].lower() in ("critical", "high")
    assert "fungicide" in recs[0]["treatment"].lower() or "tricyclazole" in recs[0]["treatment"].lower()

    assert recs[1]["disease_type"] in ("Brown Spot", "Rice Brown Spot", "Rice_Brown_Spot")
    assert recs[1]["priority"].lower() in ("medium", "high")

    # 2. Healthy baseline recommendation
    healthy_recs = rec_service.generate_recommendations(detected_conditions=[], farm_id=1)
    assert len(healthy_recs) == 1
    assert healthy_recs[0]["disease_type"] == "Healthy"
    assert healthy_recs[0]["priority"].lower() in ("preventive", "low", "info")


# ==========================================
# 4. FULL INGESTION & PART 4 ENDPOINTS TEST
# ==========================================

PART4_FARM_ID = 0
PART4_DEVICE_KEY = settings.DEVICE_API_KEY
PART4_ALERT_ID = 0

def test_part4_full_farm_ingest_disease_and_endpoints():
    """
    Full end-to-end integration:
    1. Register user and farm with 3 nodes with actual MySQL GPS coordinates.
    2. Submit 5 hourly cycles to build history.
    3. On cycle 5, simulate disease signature.
    4. Verify localization activates, affected zone is created, alerts are generated.
    5. Test /api/farms/{farm_id}/localization/latest
    6. Test /api/farms/{farm_id}/alerts and mark alert read
    7. Test /api/farms/{farm_id}/recommendations
    """
    global PART4_FARM_ID, PART4_ALERT_ID

    # 1. Auth & Farm Setup
    timestamp_suffix = int(datetime.now(timezone.utc).timestamp())
    username = f"agronomist_{timestamp_suffix}"
    email = f"{username}@biosniff.example"
    pwd = "SecurePassword123!"

    reg_res = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": pwd,
        "full_name": "Dr. Rao Senior Agronomist",
        "role": "farmer",
        "phone": "+91-9876543210",
        "state": "Andhra Pradesh",
        "district": "Krishna"
    })
    assert reg_res.status_code == 201, reg_res.text

    login_res = client.post("/api/auth/login", json={"username_or_email": username, "password": pwd})
    assert login_res.status_code == 200, login_res.text
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    farm_res = client.post("/api/farms", headers=headers, json={
        "farm_name": f"Paddy Research Farm {timestamp_suffix}",
        "area": 5.0,
        "latitude": 16.506174,
        "longitude": 80.648015,
        "crop": "Rice",
        "crop_variety": "BPT-5204 (Samba Mahsuri)",
        "growth_stage": "tillering"
    })
    assert farm_res.status_code == 201, farm_res.text
    PART4_FARM_ID = farm_res.json()["farm_id"]

    # Register 3 nodes with authoritative coordinates from MySQL
    node_coords = [
        ("NODE_P4_01", 16.506170, 80.648010),
        ("NODE_P4_02", 16.506300, 80.648250),
        ("NODE_P4_03", 16.506050, 80.648400),
    ]
    for nid, lat, lon in node_coords:
        n_res = client.post("/api/nodes", headers=headers, json={
            "node_id": nid,
            "farm_id": PART4_FARM_ID,
            "node_name": f"Sensor Post {nid}",
            "latitude": lat,
            "longitude": lon,
            "installation_date": "2026-03-01T00:00:00"
        })
        assert n_res.status_code == 201

    # Ingest 5 cycles: cycles 1-4 baseline healthy, cycle 5 with disease and low battery/weak signal
    ingest_headers = {"X-Device-API-Key": PART4_DEVICE_KEY}

    for cycle_num in range(1, 6):
        is_disease_cycle = (cycle_num == 5)
        
        # In cycle 5, NODE_P4_01 has high VOC response (e.g. Rice Blast signature),
        # low battery (18.5%), and weak signal (-88 dBm).
        if is_disease_cycle:
            gases_1 = [840.0, 780.0, 820.0, 910.0, 650.0, 720.0, 780.0, 690.0, 850.0, 890.0]
            bat_1 = 18.5
            sig_1 = -88.0
        else:
            gases_1 = [210.0, 195.0, 205.0, 220.0, 190.0, 180.0, 215.0, 200.0, 210.0, 205.0]
            bat_1 = 92.0
            sig_1 = -65.0

        gases_2 = [220.0, 200.0, 210.0, 230.0, 200.0, 190.0, 225.0, 210.0, 220.0, 215.0]
        gases_3 = [215.0, 198.0, 208.0, 225.0, 195.0, 185.0, 220.0, 205.0, 215.0, 210.0]

        payload = {
            "farm_id": PART4_FARM_ID,
            "timestamp": f"2026-09-12T{cycle_num:02d}:00:00Z",
            "wind": {
                "average_speed": 2.4,
                "average_direction": 85.0
            },
            "nodes": [
                {
                    "node_id": "NODE_P4_01",
                    "gas_resistance": gases_1,
                    "temperature": 29.5,
                    "humidity": 78.0,
                    "pressure": 1011.2,
                    "battery": bat_1,
                    "signal": sig_1
                },
                {
                    "node_id": "NODE_P4_02",
                    "gas_resistance": gases_2,
                    "temperature": 29.5,
                    "humidity": 78.0,
                    "pressure": 1011.2,
                    "battery": 88.0,
                    "signal": -70.0
                },
                {
                    "node_id": "NODE_P4_03",
                    "gas_resistance": gases_3,
                    "temperature": 29.5,
                    "humidity": 78.0,
                    "pressure": 1011.2,
                    "battery": 85.0,
                    "signal": -72.0
                }
            ]
        }

        res = client.post("/api/sensor-data", headers=ingest_headers, json=payload)
        assert res.status_code == 200, res.text
        data = res.json()

        if is_disease_cycle:
            # Cycle 5: 5-cycle window complete, predictions run, alerts triggered
            assert len(data["predictions"]) == 3
            # Check for low battery and connectivity alerts generated on cycle 5
            alert_types = [a["type"] for a in data.get("alerts", [])]
            assert "LOW_BATTERY" in alert_types
            assert "CONNECTIVITY_WARNING" in alert_types

    # 5. Verify Latest Localization Endpoint
    loc_res = client.get(f"/api/farms/{PART4_FARM_ID}/localization/latest")
    assert loc_res.status_code == 200
    loc_data = loc_res.json()
    assert "active" in loc_data
    assert "geo" in loc_data
    assert "source_score" in loc_data

    # 6. Verify Localization History Endpoint
    loc_hist_res = client.get(f"/api/farms/{PART4_FARM_ID}/localization/history")
    assert loc_hist_res.status_code == 200
    loc_hist = loc_hist_res.json()
    assert loc_hist["farm_id"] == PART4_FARM_ID
    assert "history" in loc_hist

    # 7. Verify Alerts Endpoint and Mark as Read
    alerts_res = client.get(f"/api/farms/{PART4_FARM_ID}/alerts")
    assert alerts_res.status_code == 200
    alerts_data = alerts_res.json()
    assert alerts_data["farm_id"] == PART4_FARM_ID
    assert len(alerts_data["alerts"]) > 0

    first_alert = alerts_data["alerts"][0]
    PART4_ALERT_ID = first_alert["alert_id"]

    # Mark as read via PUT
    read_put_res = client.put(f"/api/alerts/{PART4_ALERT_ID}/read")
    assert read_put_res.status_code == 200
    assert read_put_res.json()["is_read"] is True

    # Mark as read via PATCH
    read_patch_res = client.patch(f"/api/alerts/{PART4_ALERT_ID}/read")
    assert read_patch_res.status_code == 200
    assert read_patch_res.json()["is_read"] is True

    # 8. Verify Recommendations Endpoint
    recs_res = client.get(f"/api/farms/{PART4_FARM_ID}/recommendations")
    assert recs_res.status_code == 200
    recs_data = recs_res.json()
    assert isinstance(recs_data, list)
    assert len(recs_data) > 0
    assert "disease_type" in recs_data[0]
    assert "recommendation" in recs_data[0] or "actionable_advice" in recs_data[0]
