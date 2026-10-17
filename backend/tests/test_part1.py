"""
Comprehensive verification test suite for Part 1 of Bio-Sniff backend.
Uses isolated in-memory test database session to ensure complete idempotency.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

from tests.conftest import client, test_engine, TestingSessionLocal


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"


def test_auth_registration_and_login():
    # 1. Register Farmer
    reg_payload = {
        "username": "ramesh_farmer",
        "email": "ramesh.patel@agri.bio-sniff.in",
        "password": "SecurePassword123!",
        "role": "farmer",
        "full_name": "Ramesh Patel",
        "phone": "+91-9876543210",
        "state": "Gujarat",
        "district": "Anand"
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201, reg_resp.text
    reg_data = reg_resp.json()
    assert reg_data["username"] == "ramesh_farmer"
    assert reg_data["role"] == "farmer"
    assert reg_data["farmer_id"] is not None
    farmer_id = reg_data["farmer_id"]

    # 2. Login Farmer
    login_payload = {
        "username_or_email": "ramesh_farmer",
        "password": "SecurePassword123!"
    }
    login_resp = client.post("/api/auth/login", json=login_payload)
    assert login_resp.status_code == 200, login_resp.text
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["role"] == "farmer"
    assert token_data["farmer_id"] == farmer_id
    token = token_data["access_token"]

    # 3. Test /api/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["username"] == "ramesh_farmer"
    assert me_data["farmer_id"] == farmer_id


def test_farm_and_node_lifecycle():
    # Login as farmer
    login_resp = client.post("/api/auth/login", json={
        "username_or_email": "ramesh.patel@agri.bio-sniff.in",
        "password": "SecurePassword123!"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a Farm with authoritative GPS coordinates
    farm_payload = {
        "farm_name": "Green Valley Paddy Fields",
        "area": 12.5,
        "crop": "Rice (Paddy)",
        "crop_variety": "Basmati PB-1121",
        "growth_stage": "Tillering",
        "address": "Block B, Anand Agricultural Zone, Gujarat",
        "latitude": 22.5645,
        "longitude": 72.9289,
        "status": "active"
    }
    create_farm_resp = client.post("/api/farms", json=farm_payload, headers=headers)
    assert create_farm_resp.status_code == 201, create_farm_resp.text
    farm = create_farm_resp.json()
    farm_id = farm["farm_id"]
    assert farm["farm_name"] == "Green Valley Paddy Fields"
    assert farm["latitude"] == 22.5645
    assert farm["longitude"] == 72.9289

    # 2. Get farm by ID
    get_farm_resp = client.get(f"/api/farms/{farm_id}", headers=headers)
    assert get_farm_resp.status_code == 200
    assert get_farm_resp.json()["farm_name"] == "Green Valley Paddy Fields"

    # 3. Register Node 1 (Master Gateway)
    node1_payload = {
        "node_id": "node_1",
        "farm_id": farm_id,
        "node_name": "Field Sector A - Master Gateway",
        "latitude": 22.56451,
        "longitude": 72.92892,
        "is_master": True,
        "battery_percentage": 98.5,
        "signal_strength": -68.0,
        "firmware_version": "v1.2.4-mesh"
    }
    n1_resp = client.post("/api/nodes", json=node1_payload, headers=headers)
    assert n1_resp.status_code == 201, n1_resp.text
    assert n1_resp.json()["node_id"] == "node_1"
    assert n1_resp.json()["is_master"] is True

    # 4. Register Node 2 (Slave Mesh Node)
    node2_payload = {
        "node_id": "node_2",
        "farm_id": farm_id,
        "node_name": "Field Sector B - North Node",
        "latitude": 22.56580,
        "longitude": 72.92950,
        "is_master": False,
        "battery_percentage": 94.0,
        "signal_strength": -72.0,
        "firmware_version": "v1.2.4-mesh"
    }
    n2_resp = client.post("/api/nodes", json=node2_payload, headers=headers)
    assert n2_resp.status_code == 201, n2_resp.text
    assert n2_resp.json()["node_id"] == "node_2"

    # 5. Register Node 3 (Slave Mesh Node)
    node3_payload = {
        "node_id": "node_3",
        "farm_id": farm_id,
        "node_name": "Field Sector C - South Node",
        "latitude": 22.56320,
        "longitude": 72.92810,
        "is_master": False,
        "battery_percentage": 91.5,
        "signal_strength": -75.0,
        "firmware_version": "v1.2.4-mesh"
    }
    n3_resp = client.post("/api/nodes", json=node3_payload, headers=headers)
    assert n3_resp.status_code == 201, n3_resp.text
    assert n3_resp.json()["node_id"] == "node_3"

    # 6. Verify 3-Node Capacity Restriction:
    # Attempting to register a 4th node must fail with HTTP 400!
    node4_payload = {
        "node_id": "node_4",
        "farm_id": farm_id,
        "node_name": "Field Sector D - Excess Node",
        "latitude": 22.56200,
        "longitude": 72.92700,
        "is_master": False
    }
    n4_resp = client.post("/api/nodes", json=node4_payload, headers=headers)
    assert n4_resp.status_code == 400
    assert "maximum allowed capacity of 3 Bio-Sniff nodes" in n4_resp.json()["detail"]

    # 7. List Farm Nodes
    nodes_resp = client.get(f"/api/farms/{farm_id}/nodes", headers=headers)
    assert nodes_resp.status_code == 200
    nodes_list = nodes_resp.json()
    assert len(nodes_list) == 3
    node_ids = [n["node_id"] for n in nodes_list]
    assert node_ids == ["node_1", "node_2", "node_3"]

    # 8. Update Node
    update_resp = client.put(f"/api/nodes/node_2", json={"node_name": "Field Sector B - North Canopy"}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["node_name"] == "Field Sector B - North Canopy"

    # 9. Test Device API Key auth dependency directly
    from app.api.deps import verify_device_api_key
    from fastapi import HTTPException

    # Valid key
    assert verify_device_api_key(settings.DEVICE_API_KEY) == settings.DEVICE_API_KEY
    # Invalid key
    with pytest.raises(HTTPException) as exc_info:
        verify_device_api_key("invalid-dummy-key")
    assert exc_info.value.status_code == 403


if __name__ == "__main__":
    test_health_check()
    test_auth_registration_and_login()
    test_farm_and_node_lifecycle()
    print("ALL TESTS PASSED SUCCESSFULLY!")
