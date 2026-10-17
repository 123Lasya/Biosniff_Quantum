import urllib.request
import json
from datetime import datetime, timedelta, timezone

BASE_URL = "http://localhost:8000/api"
DEVICE_KEY = "esp32-master-secret-key-99a8b7c6d5e4"
HEADERS = {
    "X-Device-API-Key": DEVICE_KEY,
    "Content-Type": "application/json"
}

def post_json(url, data, headers):
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {}, method='GET')
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def test_pipeline():
    base_time = datetime.now(timezone.utc) - timedelta(hours=6)
    farm_id = 1
    
    print("--- SIMULATING INGESTION OF CYCLES C1 THROUGH C6 ---")
    
    for i in range(1, 7):
        cycle_time = (base_time + timedelta(hours=i)).isoformat()
        payload = {
            "farm_id": farm_id,
            "timestamp": cycle_time,
            "nodes": [
                {
                    "node_id": "NODE_01",
                    "gas_resistance": [120.0 + i*2 + j*0.5 for j in range(10)],
                    "temperature": 28.0 + i * 0.2,
                    "humidity": 70.0 - i * 0.5,
                    "pressure": 1008.0 + i * 0.1,
                    "battery": 95 - i,
                    "signal": -75
                },
                {
                    "node_id": "NODE_02",
                    "gas_resistance": [115.0 + i*2 + j*0.5 for j in range(10)],
                    "temperature": 28.2 + i * 0.2,
                    "humidity": 71.0 - i * 0.5,
                    "pressure": 1008.0 + i * 0.1,
                    "battery": 92 - i,
                    "signal": -78
                },
                {
                    "node_id": "NODE_03",
                    "gas_resistance": [122.0 + i*2 + j*0.5 for j in range(10)],
                    "temperature": 27.9 + i * 0.2,
                    "humidity": 69.0 - i * 0.5,
                    "pressure": 1008.5 + i * 0.1,
                    "battery": 94 - i,
                    "signal": -76
                }
            ],
            "wind": {
                "average_speed": 2.4,
                "average_direction": 48.0
            }
        }
        
        status, res_json = post_json(f"{BASE_URL}/sensor-data", payload, HEADERS)
        assert status == 200, f"Cycle {i} failed: {res_json}"
        preds_count = len(res_json.get("predictions", []))
        print(f"Cycle {i} ({cycle_time[:19]}): HTTP {status} | Predictions Generated: {preds_count}")
        if preds_count > 0:
            for p in res_json["predictions"]:
                print(f"   Node {p['node_id']}: Class = {p['predicted_class']} | Conf = {p['confidence']:.1f}%")

    print("\n--- VERIFYING FARMER DASHBOARD API ---")
    status, dash_json = get_json(f"{BASE_URL}/farmer/dashboard/{farm_id}")
    assert status == 200
    print(f"Farmer Dashboard Health Status: {dash_json['health_status']}")
    print(f"Farmer Crop: {dash_json['crop']}")
    print(f"Latest Nodes Count: {len(dash_json['latest_node_states'])}")

    print("\n✅ C1..C6 INGESTION AND PIPELINE TEST SUCCESSFUL!")

if __name__ == "__main__":
    test_pipeline()
