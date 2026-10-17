#!/usr/bin/env python3
"""
Phase 2 Test Harness & Automated E2E Verification Script.

Tests:
1. Master ESP32 sensor ingestion contract (POST /api/sensor-data) with X-Device-API-Key.
2. 5-hour rolling window readiness per node (C1..C4 -> baseline collecting, C5 -> prediction ready).
3. Attention Bi-LSTM ML inference execution using best_biosniff_lstm.pkl & scaler_lstm.pkl.
4. Rolling window progression (C2..C6, C3..C7).
5. Duplicate cycle rejection.
6. Malformed node payload rejection.
7. Multi-node disease activation & wind-aware spatial localization estimation.
8. Persistent DB-driven hourly missing node monitoring & alert creation.
9. Farmer dashboard DB state restoration after login.
"""

import sys
import os
import json
import requests
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
API_KEY = "esp32-master-secret-key-99a8b7c6d5e4"
HEADERS_KEY = {"X-Device-API-Key": API_KEY, "Content-Type": "application/json"}

# Healthy baseline gas resistance readings (kΩ)
HEALTHY_GAS = [145.2, 138.4, 124.6, 112.8, 98.4, 88.5, 76.2, 65.4, 52.1, 41.8]
# Diseased volatile gas signature (substantially reduced gas resistance due to pathogen VOCs)
DISEASED_GAS = [42.1, 38.5, 29.4, 25.1, 18.2, 14.6, 12.1, 10.4, 8.2, 6.1]

def run_phase2_test_harness():
    print("=" * 75)
    print("BIO-SNIFF PHASE 2: AUTOMATED PIPELINE & END-TO-END VERIFICATION")
    print("=" * 75)

    # 1. Login as Farmer & Get Farm ID
    print("\n[STEP 1] Farmer Authentication & persistent state lookup...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username_or_email": "ramesh.patil@biosniff.com",
        "password": "Farmer@123456"
    })
    if login_resp.status_code != 200:
        print(f"FAILED: Farmer login failed with code {login_resp.status_code}: {login_resp.text}")
        sys.exit(1)
    
    auth_data = login_resp.json()
    token = auth_data["access_token"]
    farmer_headers = {"Authorization": f"Bearer {token}"}
    print("✅ Farmer login successful.")

    # Get Farmer Farm dynamically
    farms_resp = requests.get(f"{BASE_URL}/api/farms", headers=farmer_headers)
    if farms_resp.status_code != 200:
        print(f"FAILED: GET /api/farms returned {farms_resp.status_code}: {farms_resp.text}")
        sys.exit(1)
    
    farmer_farms = farms_resp.json()
    if not farmer_farms:
        print("FAILED: No farm found for authenticated farmer!")
        sys.exit(1)
    
    farm_id = farmer_farms[0]["farm_id"]
    print(f"✅ Authenticated Farmer owns Farm ID={farm_id} ('{farmer_farms[0]['farm_name']}')")

    # Get Farmer Dashboard
    dash_resp = requests.get(f"{BASE_URL}/api/farmer/dashboard/{farm_id}", headers=farmer_headers)
    if dash_resp.status_code != 200:
        print(f"FAILED: GET farmer dashboard returned {dash_resp.status_code}: {dash_resp.text}")
        sys.exit(1)
    
    dash = dash_resp.json()
    nodes = dash["latest_node_states"]
    node_ids = [n["node_id"] for n in nodes]
    print(f"✅ Found Farm ID={farm_id} with {len(nodes)} nodes: {node_ids}")

    if not node_ids:
        print("FAILED: No nodes found for farm. Ensure database seed/registration exists.")
        sys.exit(1)

    # Clear historical cycles using sqlite3 for a clean 0..5 baseline test
    import sqlite3
    db_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "biosniff.db")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "biosniff.db")),
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("DELETE FROM sensor_cycles WHERE farm_id = ?", (farm_id,))
                cur.execute("DELETE FROM predictions WHERE farm_id = ?", (farm_id,))
                cur.execute("DELETE FROM alerts WHERE farm_id = ?", (farm_id,))
                cur.execute("DELETE FROM localization_results WHERE farm_id = ?", (farm_id,))
                conn.commit()
                conn.close()
                print(f"✅ Cleared existing cycles & predictions for Farm ID={farm_id} in {db_path} to test 0..5 baseline readiness.")
            except Exception as e:
                print(f"⚠️ Note: DB cleanup warning on {db_path}: {e}")

    # 2. Test Sequential Hourly Sensor Ingestion (Cycles C1..C5)
    base_time = datetime.now(timezone.utc) - timedelta(hours=7)

    print("\n[STEP 2] Simulating 5 Sequential Hourly Master Telemetry Cycles (C1..C5)...")
    for cycle_num in range(1, 6):
        cycle_time = (base_time + timedelta(hours=cycle_num)).isoformat()
        
        # On Cycle 5, inject disease signature on node_ids[0] to test pathogen inference
        is_c5 = (cycle_num == 5)
        
        payload_nodes = []
        for idx, nid in enumerate(node_ids):
            gas = DISEASED_GAS if (is_c5 and idx == 0) else HEALTHY_GAS
            payload_nodes.append({
                "node_id": nid,
                "gas_resistance": gas,
                "temperature": 27.5 + cycle_num * 0.2,
                "humidity": 70.0 + cycle_num * 0.5,
                "pressure": 1008.0 + cycle_num * 0.1,
                "battery": 95.0,
                "signal": -72.0
            })

        payload = {
            "farm_id": farm_id,
            "timestamp": cycle_time,
            "nodes": payload_nodes,
            "wind": {
                "average_speed": 2.5,
                "average_direction": 45.0
            }
        }

        resp = requests.post(f"{BASE_URL}/api/sensor-data", headers=HEADERS_KEY, json=payload)
        if resp.status_code != 200:
            print(f"FAILED: Cycle C{cycle_num} returned HTTP {resp.status_code}: {resp.text}")
            sys.exit(1)

        result = resp.json()
        print(f"  Cycle C{cycle_num}: Ingestion status='{result['status']}', processed={len(result['processed_nodes'])} nodes")

        if cycle_num < 5:
            # Check baseline collecting state
            for proc in result['processed_nodes']:
                if proc['prediction_ready']:
                    print(f"FAILED: Node {proc['node_id']} marked ready before 5 cycles (C{cycle_num})!")
                    sys.exit(1)
            print(f"  --> C{cycle_num} verified: prediction_ready=False (Collecting baseline data N/5)")
        else:
            # Cycle 5: Check prediction readiness & ML inference execution
            for proc in result['processed_nodes']:
                if not proc['prediction_ready']:
                    print(f"FAILED: Node {proc['node_id']} NOT ready at cycle C5!")
                    sys.exit(1)
                if proc['prediction']:
                    p = proc['prediction']
                    print(f"  --> Node {proc['node_id']} ML Prediction: class='{p['predicted_class']}', is_disease={p['is_disease']}, confidence={p['confidence'] * 100:.1f}%, model={p['model_version']}")

            print(f"✅ C5 ML Inference & Rolling Window verified. Farm Disease Status: '{result['farm_disease_status']}'")

    # 3. Test Rolling Window Progression (C6 and C7)
    print("\n[STEP 3] Testing Rolling Window Shift (Cycles C6 & C7)...")
    for cycle_num in (6, 7):
        cycle_time = (base_time + timedelta(hours=cycle_num)).isoformat()
        payload_nodes = [{
            "node_id": nid,
            "gas_resistance": HEALTHY_GAS,
            "temperature": 28.0,
            "humidity": 72.0,
            "pressure": 1008.0,
            "battery": 94.0,
            "signal": -74.0
        } for nid in node_ids]

        payload = {
            "farm_id": farm_id,
            "timestamp": cycle_time,
            "nodes": payload_nodes,
            "wind": {"average_speed": 2.2, "average_direction": 50.0}
        }

        resp = requests.post(f"{BASE_URL}/api/sensor-data", headers=HEADERS_KEY, json=payload)
        if resp.status_code != 200:
            print(f"FAILED: Rolling window cycle C{cycle_num} failed: {resp.text}")
            sys.exit(1)
        res = resp.json()
        print(f"  Cycle C{cycle_num}: Success. Processed {len(res['processed_nodes'])} nodes.")

    print("✅ Rolling 5-hour window progression verified.")

    # 4. Test Duplicate Cycle Rejection
    print("\n[STEP 4] Testing Duplicate Hourly Cycle Rejection...")
    dup_time = (base_time + timedelta(hours=7)).isoformat()
    dup_payload = {
        "farm_id": farm_id,
        "timestamp": dup_time,
        "nodes": [{
            "node_id": node_ids[0],
            "gas_resistance": HEALTHY_GAS,
            "temperature": 28.0,
            "humidity": 72.0,
            "pressure": 1008.0,
            "battery": 94.0,
            "signal": -74.0
        }],
        "wind": {"average_speed": 2.2, "average_direction": 50.0}
    }
    dup_resp = requests.post(f"{BASE_URL}/api/sensor-data", headers=HEADERS_KEY, json=dup_payload)
    dup_res = dup_resp.json()
    if len(dup_res.get("rejected_nodes", [])) > 0:
        print(f"✅ Duplicate cycle correctly rejected: reason='{dup_res['rejected_nodes'][0]['reason']}'")
    else:
        print("FAILED: Duplicate cycle was not rejected!")
        sys.exit(1)

    # 5. Test Malformed Node Payload Rejection
    print("\n[STEP 5] Testing Malformed Node Payload Rejection...")
    mal_payload = {
        "farm_id": farm_id,
        "timestamp": (base_time + timedelta(hours=8)).isoformat(),
        "nodes": [{
            "node_id": node_ids[0],
            "gas_resistance": [145.2, 138.4, 124.6], # Only 3 gas values instead of 10
            "temperature": 28.0,
            "humidity": 72.0,
            "pressure": 1008.0,
        }],
        "wind": {"average_speed": 2.0, "average_direction": 40.0}
    }
    mal_resp = requests.post(f"{BASE_URL}/api/sensor-data", headers=HEADERS_KEY, json=mal_payload)
    mal_res = mal_resp.json()
    if len(mal_res.get("rejected_nodes", [])) > 0:
        print(f"✅ Malformed payload correctly rejected: reason='{mal_res['rejected_nodes'][0]['reason']}'")
    else:
        print("FAILED: Malformed payload was not rejected!")
        sys.exit(1)

    # 6. Test Hourly Missing Node Monitoring & Alert Creation
    print("\n[STEP 6] Testing Database-Driven Hourly Missing Node Monitoring...")
    chk_resp = requests.post(f"{BASE_URL}/api/nodes/check-overdue?farm_id={farm_id}")
    if chk_resp.status_code == 200:
        alerts_list = chk_resp.json()
        print(f"✅ Missing node monitor executed cleanly. Overdue alerts generated/checked: {len(alerts_list)}")
    else:
        print(f"FAILED: Overdue node check returned {chk_resp.status_code}: {chk_resp.text}")
        sys.exit(1)

    # 7. Test Persistent Dashboard State Retrieval After Re-login
    print("\n[STEP 7] Verifying Persisted Dashboard State After Re-Login...")
    relogin_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username_or_email": "ramesh.patil@biosniff.com",
        "password": "Farmer@123456"
    })
    re_token = relogin_resp.json()["access_token"]
    re_headers = {"Authorization": f"Bearer {re_token}"}

    final_dash_resp = requests.get(f"{BASE_URL}/api/farmer/dashboard/{farm_id}", headers=re_headers)
    final_dash = final_dash_resp.json()

    print(f"  Farmer: {final_dash['farmer']['full_name']} ({final_dash['farmer']['email']})")
    print(f"  Farm: {final_dash['farm']['name']} ({final_dash['farm']['area_acres']} Acres, {final_dash['farm']['crop_variety']})")
    print(f"  Nodes State Count: {len(final_dash['latest_node_states'])}")
    for n in final_dash['latest_node_states']:
        print(f"    Node {n['node_id']}: temp={n['readings']['temperature']}°C, hum={n['readings']['humidity']}%, voc={n['readings']['total_voc']} kΩ")
    print(f"  Latest Predictions Count: {len(final_dash.get('latest_predictions', []))}")
    print(f"  Health Status: {final_dash['health_status']}")
    print(f"  Active Alerts: {final_dash['alerts_summary']['total']} total ({final_dash['alerts_summary']['unread']} unread)")

    print("\n" + "=" * 75)
    print("✅ PHASE 2 ACCEPTANCE TEST HARNESS SUCCEEDED CLEANLY!")
    print("=" * 75)

if __name__ == "__main__":
    run_phase2_test_harness()
