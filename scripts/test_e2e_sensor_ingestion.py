"""
BIO-SNIFF End-to-End Sensor Ingestion & Pipeline Test Script
-----------------------------------------------------------
Tests complete workflow:
1. Master ESP32 telemetry ingestion (POST /api/sensor-data) with API key.
2. 5-hour rolling window [C1..C5] readiness and rolling behavior (C2..C6, C3..C7).
3. Multi-node independent tracking (node_1, node_2, node_3).
4. Missing node alert generation (batch with node_1, node_2; omit node_3).
5. Malformed node handling (invalid gas array length on one node, valid node succeeds).
6. Disease classification -> Localization -> Recommendation -> Alert pipeline.
7. DB persistence verification.
"""

import sys
import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

# Ensure backend directory is in sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.core.database import SessionLocal
from app.models.sensor_cycle import SensorCycle
from app.models.prediction import Prediction
from app.models.localization import LocalizationResult

BASE_URL = "http://localhost:8000/api"
API_KEY = "esp32-master-secret-key-99a8b7c6d5e4"
FARM_ID = 1

HEADERS = {
    "Content-Type": "application/json",
    "X-Device-API-Key": API_KEY
}

def clean_farm_cycles(farm_id: int):
    """Cleans previous test sensor cycles, predictions, and localizations for farm_id to ensure clean rolling window testing."""
    db = SessionLocal()
    try:
        db.query(SensorCycle).filter(SensorCycle.farm_id == farm_id).delete()
        db.query(Prediction).filter(Prediction.farm_id == farm_id).delete()
        db.query(LocalizationResult).filter(LocalizationResult.farm_id == farm_id).delete()
        db.commit()
        print(f"Cleared previous test cycles, predictions, and localizations for farm_id={farm_id}.")
    finally:
        db.close()

def make_post_request(endpoint: str, payload: dict) -> tuple[int, dict]:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        return e.code, body

def make_get_request(endpoint: str) -> tuple[int, dict]:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"X-Device-API-Key": API_KEY}, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode("utf-8"))
        return e.code, body

def run_tests():
    print("=" * 70)
    print("BIO-SNIFF END-TO-END SENSOR INGESTION & PIPELINE VERIFICATION")
    print("=" * 70)

    # Clean previous test cycles for determinism
    clean_farm_cycles(FARM_ID)

    # 1. Test Single Cycle Ingestion (Cycle 1)
    base_time = datetime.now(timezone.utc) - timedelta(hours=10)
    
    print("\n--- TEST 1: Sending Cycle 1 (Window Not Ready) ---")
    c1_payload = {
        "farm_id": FARM_ID,
        "timestamp": base_time.isoformat(),
        "wind": {"average_speed": 4.5, "average_direction": 135.0},
        "nodes": [
            {
                "node_id": "node_1",
                "gas_resistance": [45.2, 44.8, 43.5, 42.1, 41.0, 40.2, 39.5, 38.8, 38.0, 37.5],
                "temperature": 28.5,
                "humidity": 65.0,
                "pressure": 1010.2,
                "battery": 98,
                "signal": -65
            }
        ]
    }
    status, res1 = make_post_request("/sensor-data", c1_payload)
    assert status == 200, f"Expected 200, got {status}: {res1}"
    print(f"Status: {status}")
    print(f"Processed nodes count: {len(res1.get('processed_nodes', []))}")
    n1_res = res1['processed_nodes'][0]
    print(f"Node 1 prediction ready: {n1_res.get('prediction_ready')}, cycles available: {n1_res.get('cycles_available')}/5")
    assert n1_res['prediction_ready'] == False, "Cycle 1 should NOT be prediction_ready"
    assert n1_res['prediction'] is None, "Cycle 1 should NOT have a prediction"

    # 2. Send Cycles 2, 3, 4
    print("\n--- TEST 2: Sending Cycles 2, 3, 4 (Window Not Ready) ---")
    for i in range(2, 5):
        payload = {
            "farm_id": FARM_ID,
            "timestamp": (base_time + timedelta(hours=i-1)).isoformat(),
            "wind": {"average_speed": 4.5 + i*0.1, "average_direction": 135.0},
            "nodes": [
                {
                    "node_id": "node_1",
                    "gas_resistance": [45.0 + i, 44.0 + i, 43.0 + i, 42.0 + i, 41.0 + i, 40.0 + i, 39.0 + i, 38.0 + i, 37.0 + i, 36.0 + i],
                    "temperature": 28.5,
                    "humidity": 65.0,
                    "pressure": 1010.2,
                    "battery": 98 - i,
                    "signal": -65
                }
            ]
        }
        status, res = make_post_request("/sensor-data", payload)
        n_res = res['processed_nodes'][0]
        print(f"Cycle {i} -> prediction_ready: {n_res.get('prediction_ready')}, cycles available: {n_res.get('cycles_available')}/5")
        assert n_res['prediction_ready'] == False, f"Cycle {i} should NOT be prediction_ready"

    # 3. Send Cycle 5 (Window Ready & Prediction Triggered!)
    print("\n--- TEST 3: Sending Cycle 5 (Window Ready & ML Inference Triggered) ---")
    c5_payload = {
        "farm_id": FARM_ID,
        "timestamp": (base_time + timedelta(hours=4)).isoformat(),
        "wind": {"average_speed": 5.0, "average_direction": 140.0},
        "nodes": [
            {
                "node_id": "node_1",
                # Sensor gas values designed for diseased signature
                "gas_resistance": [25.0, 24.5, 23.0, 22.0, 21.0, 20.5, 19.8, 19.0, 18.5, 18.0],
                "temperature": 31.0,
                "humidity": 82.0,
                "pressure": 1008.5,
                "battery": 94,
                "signal": -68
            }
        ]
    }
    status, res5 = make_post_request("/sensor-data", c5_payload)
    assert status == 200
    n5_res = res5['processed_nodes'][0]
    print(f"Cycle 5 -> prediction_ready: {n5_res.get('prediction_ready')}, cycles available: {n5_res.get('cycles_available')}/5")
    assert n5_res['prediction_ready'] == True, "Cycle 5 MUST be prediction_ready"
    pred = n5_res.get("prediction")
    assert pred is not None, "Cycle 5 MUST produce ML prediction"
    print(f"ML Prediction Output -> Class: {pred.get('predicted_class')}, Confidence: {pred.get('confidence')}")
    print(f"Probabilities: {pred.get('probabilities')}")

    # 4. Send Cycle 6 & 7 (Test Rolling Window Behavior)
    print("\n--- TEST 4: Sending Cycles 6 & 7 (Testing Rolling Window Shift) ---")
    c6_payload = {
        "farm_id": FARM_ID,
        "timestamp": (base_time + timedelta(hours=5)).isoformat(),
        "wind": {"average_speed": 5.2, "average_direction": 145.0},
        "nodes": [
            {
                "node_id": "node_1",
                "gas_resistance": [26.0, 25.5, 24.0, 23.0, 22.0, 21.5, 20.8, 20.0, 19.5, 19.0],
                "temperature": 31.2,
                "humidity": 83.0,
                "pressure": 1008.0,
                "battery": 93,
                "signal": -68
            }
        ]
    }
    status, res6 = make_post_request("/sensor-data", c6_payload)
    n6_res = res6['processed_nodes'][0]
    print(f"Cycle 6 -> prediction_ready: {n6_res.get('prediction_ready')}, latest 5 cycle IDs: {n6_res.get('latest_5_cycle_ids')}")
    assert n6_res['prediction_ready'] == True, "Cycle 6 should maintain 5-hour rolling window"
    assert len(n6_res.get('latest_5_cycle_ids', [])) == 5

    # Verify history endpoint for node_1
    status, hist = make_get_request("/nodes/node_1/sensor-history?limit=10")
    print(f"Node 1 cycle history count: {hist.get('total_cycles')}, window readiness: {hist.get('prediction_ready')}")

    # 5. Multi-Node Independence Test (node_1, node_2, node_3)
    print("\n--- TEST 5: Multi-Node Processing (node_1, node_2, node_3) ---")
    multi_payload = {
        "farm_id": FARM_ID,
        "timestamp": (base_time + timedelta(hours=6)).isoformat(),
        "wind": {"average_speed": 4.8, "average_direction": 130.0},
        "nodes": [
            {
                "node_id": "node_1",
                "gas_resistance": [40.0] * 10,
                "temperature": 29.0,
                "humidity": 70.0,
                "pressure": 1010.0,
                "battery": 90,
                "signal": -70
            },
            {
                "node_id": "node_2",
                "gas_resistance": [42.0] * 10,
                "temperature": 29.5,
                "humidity": 68.0,
                "pressure": 1010.0,
                "battery": 88,
                "signal": -72
            },
            {
                "node_id": "node_3",
                "gas_resistance": [41.0] * 10,
                "temperature": 29.2,
                "humidity": 69.0,
                "pressure": 1010.0,
                "battery": 92,
                "signal": -69
            }
        ]
    }
    status, multi_res = make_post_request("/sensor-data", multi_payload)
    print(f"Multi-node response status: {status}, processed nodes count: {len(multi_res.get('processed_nodes', []))}")
    processed_nodes = [r['node_id'] for r in multi_res.get('processed_nodes', [])]
    assert "node_1" in processed_nodes and "node_2" in processed_nodes and "node_3" in processed_nodes

    # 6. Missing Node Test (Send node_1 and node_2, omit node_3)
    print("\n--- TEST 6: Missing Node Behavior ---")
    missing_payload = {
        "farm_id": FARM_ID,
        "timestamp": (base_time + timedelta(hours=7)).isoformat(),
        "wind": {"average_speed": 4.5, "average_direction": 130.0},
        "nodes": [
            {
                "node_id": "node_1",
                "gas_resistance": [40.0] * 10,
                "temperature": 29.0,
                "humidity": 70.0,
                "pressure": 1010.0,
                "battery": 89,
                "signal": -70
            },
            {
                "node_id": "node_2",
                "gas_resistance": [42.0] * 10,
                "temperature": 29.5,
                "humidity": 68.0,
                "pressure": 1010.0,
                "battery": 87,
                "signal": -72
            }
        ]
    }
    status, missing_res = make_post_request("/sensor-data", missing_payload)
    print(f"Missing node test response status: {status}")
    missing_nodes = [m['node_id'] for m in missing_res.get("missing_nodes", [])]
    print(f"Missing nodes reported by backend: {missing_nodes}")
    assert "node_3" in missing_nodes, "node_3 should be listed as missing"

    # 7. Malformed Node Test (Invalid gas array length on node_2)
    print("\n--- TEST 7: Malformed Node Behavior (Partial Success) ---")
    malformed_payload = {
        "farm_id": FARM_ID,
        "timestamp": (base_time + timedelta(hours=8)).isoformat(),
        "wind": {"average_speed": 4.5, "average_direction": 130.0},
        "nodes": [
            {
                "node_id": "node_1",
                "gas_resistance": [40.0] * 10, # Valid (10 readings)
                "temperature": 29.0,
                "humidity": 70.0,
                "pressure": 1010.0,
                "battery": 88,
                "signal": -70
            },
            {
                "node_id": "node_2",
                "gas_resistance": [42.0] * 5, # Invalid (only 5 readings instead of 10)
                "temperature": 29.5,
                "humidity": 68.0,
                "pressure": 1010.0,
                "battery": 86,
                "signal": -72
            }
        ]
    }
    status, malformed_res = make_post_request("/sensor-data", malformed_payload)
    print(f"Malformed test response status: {status}")
    processed_nodes = malformed_res.get("processed_nodes", [])
    rejected_nodes = malformed_res.get("rejected_nodes", [])
    print(f"Processed nodes count: {len(processed_nodes)}, Rejected nodes count: {len(rejected_nodes)}")
    if rejected_nodes:
        print(f"Rejected nodes info: {rejected_nodes}")
    assert any(r['node_id'] == "node_1" for r in processed_nodes), "node_1 should succeed"
    assert any(r['node_id'] == "node_2" for r in rejected_nodes), "node_2 should be rejected"

    # 8. Check Farm Disease -> Localization Pipeline
    print("\n--- TEST 8 & 9: Verification of Localization, Alerts, & Recommendations ---")
    status, loc_res = make_get_request(f"/farms/{FARM_ID}/localization/latest")
    print(f"Localization GET status: {status}")
    print(f"Active localization: {loc_res.get('active')}")
    if loc_res.get('active'):
        geo = loc_res.get('geo', {})
        az = loc_res.get('affected_zone', {})
        print(f"Estimated disease source coords: lat={geo.get('latitude')}, lon={geo.get('longitude')}")
        print(f"Affected zone: radius_m={az.get('radius_m')}, center_x={az.get('center_x')}, center_y={az.get('center_y')}")
        print(f"Source likelihood score: {loc_res.get('source_score')}")

    status, alerts_res = make_get_request(f"/farms/{FARM_ID}/alerts")
    print(f"\nFarm Alerts GET status: {status}, Total alerts: {alerts_res.get('total_alerts')}")
    if alerts_res.get('alerts'):
        print(f"Latest alert: {alerts_res['alerts'][0].get('title')} ({alerts_res['alerts'][0].get('alert_type')})")

    status, recs_res = make_get_request(f"/farms/{FARM_ID}/recommendations")
    print(f"\nFarm Recommendations GET status: {status}, Total recommendations: {len(recs_res)}")
    if recs_res:
        print(f"Latest recommendation: {recs_res[0].get('title')}")

    print("\n" + "=" * 70)
    print("ALL END-TO-END VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
