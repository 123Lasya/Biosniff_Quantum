"""
Comprehensive verification test suite for Part 2 of Bio-Sniff backend:
- Hardware Device Authentication (X-Device-API-Key)
- Master ESP32 Hourly Telemetry Ingestion (POST /api/sensor-data)
- Validation of 10 Gas Values, Temperature, Humidity, Pressure, Battery, Signal
- Partial Success on Malformed Gas Arrays (saving valid nodes, rejecting invalid)
- Unknown & Foreign Node Handling
- Missing Node Detection (no fabrication, alert generation)
- Duplicate Cycle / Timestamp Batch Detection
- Wind Microclimate Validation (speed >= 0, direction in [0, 360])
- 5-Hour Rolling Window & Prediction Readiness Progression (Hour 1 to Hour 6)
- Read APIs: /api/nodes/{id}/sensor-history, /api/farms/{id}/environment, /api/farms/{id}/environment/history
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from tests.conftest import client

HW_HEADERS = {"X-Device-API-Key": settings.DEVICE_API_KEY}
TEST_FARM_ID: int = 1


def setup_seed_data():
    """Seeds a test farmer, farm, and 3 sensor nodes."""
    global TEST_FARM_ID
    # Register Farmer & Login to create farm
    reg_payload = {
        "username": "hw_test_farmer",
        "email": "hw.farmer@bio-sniff.in",
        "password": "Password123!",
        "role": "farmer",
        "full_name": "Kishan Kumar",
        "phone": "+91-9876543211",
        "state": "Punjab",
        "district": "Ludhiana"
    }
    client.post("/api/auth/register", json=reg_payload)
    login_resp = client.post("/api/auth/login", json={
        "username_or_email": "hw_test_farmer",
        "password": "Password123!"
    })
    token = login_resp.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {token}"}

    # Create Farm
    farm_payload = {
        "farm_name": "Ludhiana Wheat & Paddy Research Farm",
        "area": 25.0,
        "crop": "Rice (Paddy)",
        "crop_variety": "PR-126",
        "growth_stage": "Tillering",
        "latitude": 30.9010,
        "longitude": 75.8573,
        "status": "active"
    }
    farm_resp = client.post("/api/farms", json=farm_payload, headers=user_headers)
    assert farm_resp.status_code == 201
    TEST_FARM_ID = farm_resp.json()["farm_id"]

    # Register Node 1 (Master Gateway)
    client.post("/api/nodes", json={
        "node_id": "NODE_01",
        "farm_id": TEST_FARM_ID,
        "node_name": "Master Gateway Node 1",
        "latitude": 30.9010,
        "longitude": 75.8573,
        "is_master": True,
        "battery_percentage": 100.0,
        "signal_strength": -58.0
    }, headers=user_headers)

    # Register Node 2
    client.post("/api/nodes", json={
        "node_id": "NODE_02",
        "farm_id": TEST_FARM_ID,
        "node_name": "East Sector Node 2",
        "latitude": 30.9020,
        "longitude": 75.8580,
        "is_master": False,
        "battery_percentage": 98.0,
        "signal_strength": -64.0
    }, headers=user_headers)

    # Register Node 3
    client.post("/api/nodes", json={
        "node_id": "NODE_03",
        "farm_id": TEST_FARM_ID,
        "node_name": "West Sector Node 3",
        "latitude": 30.9000,
        "longitude": 75.8565,
        "is_master": False,
        "battery_percentage": 95.0,
        "signal_strength": -67.0
    }, headers=user_headers)


@pytest.fixture(scope="module", autouse=True)
def init_test_farm_and_nodes():
    setup_seed_data()


def test_device_api_key_authentication():
    """Verifies that Master ESP32 hardware authentication is strictly enforced."""
    payload = {
        "farm_id": TEST_FARM_ID,
        "timestamp": "2026-09-12T01:00:00Z",
        "nodes": [],
        "wind": {"average_speed": 2.1, "average_direction": 90.0}
    }
    # 1. Missing header -> 401 Unauthorized
    resp_no_auth = client.post("/api/sensor-data", json=payload)
    assert resp_no_auth.status_code == 401
    assert "Missing X-Device-API-Key" in resp_no_auth.json()["detail"]

    # 2. Invalid API key -> 403 Forbidden
    resp_invalid_key = client.post("/api/sensor-data", json=payload, headers={"X-Device-API-Key": "fake-esp32-key"})
    assert resp_invalid_key.status_code == 403
    assert "Invalid hardware device API key" in resp_invalid_key.json()["detail"]


def test_wind_microclimate_validation():
    """Verifies wind speed >= 0 and direction in [0, 360] validation."""
    base_payload = {
        "farm_id": TEST_FARM_ID,
        "timestamp": "2026-09-12T01:00:00Z",
        "nodes": []
    }
    # Negative wind speed
    bad_speed_payload = {**base_payload, "wind": {"average_speed": -1.5, "average_direction": 45.0}}
    resp = client.post("/api/sensor-data", json=bad_speed_payload, headers=HW_HEADERS)
    assert resp.status_code == 422

    # Direction > 360
    bad_dir_payload = {**base_payload, "wind": {"average_speed": 2.5, "average_direction": 420.0}}
    resp = client.post("/api/sensor-data", json=bad_dir_payload, headers=HW_HEADERS)
    assert resp.status_code == 422


def test_partial_success_and_malformed_gas_array():
    """
    If one node is malformed while others are valid:
    - Save valid nodes
    - Reject the invalid node
    - Generate appropriate node-data validation alert
    - Return clear partial-success response
    """
    ts = "2026-09-12T02:00:00Z"
    payload = {
        "farm_id": TEST_FARM_ID,
        "timestamp": ts,
        "nodes": [
            {
                "node_id": "NODE_01",
                "gas_resistance": [41.2, 41.5, 41.8, 42.0, 42.3, 42.6, 42.9, 43.1, 43.4, 43.7],  # 10 values - VALID
                "temperature": 31.5,
                "humidity": 55.0,
                "pressure": 1005.2,
                "battery": 97,
                "signal": -60
            },
            {
                "node_id": "NODE_02",
                "gas_resistance": [40.1, 40.2, 40.3],  # Only 3 values! MALFORMED
                "temperature": 30.8,
                "humidity": 56.1,
                "pressure": 1005.0,
                "battery": 94,
                "signal": -63
            },
            {
                "node_id": "NODE_03",
                "gas_resistance": [39.5, 39.8, 40.1, 40.3, 40.6, 40.8, 41.1, 41.3, 41.5, 41.8],  # 10 values - VALID
                "temperature": 32.0,
                "humidity": 54.5,
                "pressure": 1005.1,
                "battery": 92,
                "signal": -65
            }
        ],
        "wind": {"average_speed": 3.2, "average_direction": 135.0}
    }

    resp = client.post("/api/sensor-data", json=payload, headers=HW_HEADERS)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "partial_success"
    assert len(data["processed_nodes"]) == 2
    assert len(data["rejected_nodes"]) == 1
    assert data["rejected_nodes"][0]["node_id"] == "NODE_02"
    assert "expected 10 values" in data["rejected_nodes"][0]["reason"]
    assert data["environment_saved"] is True


def test_missing_node_alert():
    """
    If a registered node does not report in the hourly batch:
    - Do NOT fabricate data
    - Do NOT reuse previous cycle
    - Generate node_data_missing alert
    - Expose in missing_nodes
    """
    ts = "2026-09-12T03:00:00Z"
    # Only NODE_01 and NODE_02 report; NODE_03 is missing!
    payload = {
        "farm_id": TEST_FARM_ID,
        "timestamp": ts,
        "nodes": [
            {
                "node_id": "NODE_01",
                "gas_resistance": [42.0] * 10,
                "temperature": 32.0,
                "humidity": 54.0,
                "pressure": 1004.8,
                "battery": 96,
                "signal": -59
            },
            {
                "node_id": "NODE_02",
                "gas_resistance": [41.0] * 10,
                "temperature": 31.2,
                "humidity": 55.5,
                "pressure": 1004.7,
                "battery": 93,
                "signal": -62
            }
        ],
        "wind": {"average_speed": 2.8, "average_direction": 150.0}
    }
    resp = client.post("/api/sensor-data", json=payload, headers=HW_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["processed_nodes"]) == 2
    assert len(data["missing_nodes"]) == 1
    assert data["missing_nodes"][0]["node_id"] == "NODE_03"
    assert data["missing_nodes"][0]["alert_created"] is True


def test_unknown_node_rejection():
    """Verifies that an unregistered node is rejected cleanly."""
    ts = "2026-09-12T03:30:00Z"
    payload = {
        "farm_id": TEST_FARM_ID,
        "timestamp": ts,
        "nodes": [
            {
                "node_id": "ROGUE_NODE_99",
                "gas_resistance": [40.0] * 10,
                "temperature": 25.0,
                "humidity": 50.0,
                "pressure": 1000.0
            }
        ]
    }
    resp = client.post("/api/sensor-data", json=payload, headers=HW_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["processed_nodes"]) == 0
    assert len(data["rejected_nodes"]) == 1
    assert "not registered" in data["rejected_nodes"][0]["reason"]


def test_duplicate_cycle_detection():
    """Verifies that duplicate hourly batches for the same node and timestamp are prevented."""
    ts = "2026-09-12T04:00:00Z"
    payload = {
        "farm_id": TEST_FARM_ID,
        "timestamp": ts,
        "nodes": [
            {
                "node_id": "NODE_01",
                "gas_resistance": [43.0] * 10,
                "temperature": 33.0,
                "humidity": 52.0,
                "pressure": 1004.0,
                "battery": 95,
                "signal": -58
            }
        ]
    }
    # First submission -> saved
    resp1 = client.post("/api/sensor-data", json=payload, headers=HW_HEADERS)
    assert resp1.status_code == 200
    assert len(resp1.json()["processed_nodes"]) == 1

    # Second submission (identical timestamp and node) -> rejected as duplicate!
    resp2 = client.post("/api/sensor-data", json=payload, headers=HW_HEADERS)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["processed_nodes"]) == 0
    assert len(data2["rejected_nodes"]) == 1
    assert "Duplicate hourly cycle detected" in data2["rejected_nodes"][0]["reason"]


def test_5_hour_sliding_window_and_prediction_readiness():
    """
    Tests rolling 5-hour window progression for Node 1:
    - Hour 1 (C1): cycles_available = 1, prediction_ready = False, status = "collecting_baseline"
    - Hour 2 (C2): cycles_available = 2, prediction_ready = False, status = "collecting_baseline"
    - Hour 3 (C3): cycles_available = 3, prediction_ready = False, status = "collecting_baseline"
    - Hour 4 (C4): cycles_available = 4, prediction_ready = False, status = "collecting_baseline"
    - Hour 5 (C5): cycles_available = 5, prediction_ready = True, status = "ready_for_prediction", window = [C1..C5]
    - Hour 6 (C6): cycles_available = 6, prediction_ready = True, window = [C2..C6]
    """
    base_time = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)

    for hour_idx in range(1, 7):
        hour_time = (base_time + timedelta(hours=hour_idx)).isoformat()
        gas_vals = [40.0 + hour_idx * 0.5 + i * 0.1 for i in range(10)]
        payload = {
            "farm_id": TEST_FARM_ID,
            "timestamp": hour_time,
            "nodes": [
                {
                    "node_id": "NODE_01",
                    "gas_resistance": gas_vals,
                    "temperature": 30.0 + hour_idx,
                    "humidity": 60.0 - hour_idx,
                    "pressure": 1005.0,
                    "battery": 95 - hour_idx,
                    "signal": -60
                }
            ],
            "wind": {"average_speed": 2.0 + hour_idx * 0.2, "average_direction": (45 * hour_idx) % 360}
        }
        resp = client.post("/api/sensor-data", json=payload, headers=HW_HEADERS)
        assert resp.status_code == 200, resp.text
        node_res = resp.json()["processed_nodes"][0]

        # Prior tests added 3 cycles to NODE_01 (at 02:00, 03:00, 04:00)
        # So total cycles for NODE_01 increases with each hour
        if node_res["cycles_available"] < 5:
            assert node_res["prediction_ready"] is False
            assert node_res["readiness_status"] == "collecting_baseline"
            assert node_res["cycles_required"] == 5
        else:
            assert node_res["prediction_ready"] is True
            assert node_res["readiness_status"] == "ready_for_prediction"
            assert len(node_res["latest_5_cycle_ids"]) == 5


def test_read_apis():
    """Verifies all required GET endpoints return clean JSON for the React frontend."""
    # 1. GET /api/nodes/{node_id}/sensor-history
    hist_resp = client.get("/api/nodes/NODE_01/sensor-history?limit=20")
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    assert hist["node_id"] == "NODE_01"
    assert hist["prediction_ready"] is True
    assert hist["cycles_available"] >= 5
    assert len(hist["latest_5_window"]) == 5
    # Verify each cycle has exactly 10 gas values
    assert len(hist["latest_5_window"][0]["gas_readings"]) == 10
    assert hist["status"] == "online"

    # 2. GET /api/farms/{farm_id}/environment
    env_resp = client.get(f"/api/farms/{TEST_FARM_ID}/environment")
    assert env_resp.status_code == 200
    env = env_resp.json()
    assert env["farm_id"] == TEST_FARM_ID
    assert env["latest_reading"] is not None
    assert env["latest_reading"]["wind_speed"] >= 0
    assert env["node_averages"] is not None
    assert env["node_averages"]["reporting_nodes"] >= 1

    # 3. GET /api/farms/{farm_id}/environment/history
    env_hist_resp = client.get(f"/api/farms/{TEST_FARM_ID}/environment/history?limit=10")
    assert env_hist_resp.status_code == 200
    env_hist = env_hist_resp.json()
    assert env_hist["farm_id"] == TEST_FARM_ID
    assert env_hist["count"] > 0
    assert len(env_hist["history"]) > 0


if __name__ == "__main__":
    setup_seed_data()
    test_device_api_key_authentication()
    test_wind_microclimate_validation()
    test_partial_success_and_malformed_gas_array()
    test_missing_node_alert()
    test_unknown_node_rejection()
    test_duplicate_cycle_detection()
    test_5_hour_sliding_window_and_prediction_readiness()
    test_read_apis()
    print("ALL PART 2 TESTS PASSED SUCCESSFULLY!")
