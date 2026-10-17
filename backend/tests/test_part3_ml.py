"""
Unit and integration tests for Part 3:
- Attention Bi-LSTM model architecture and evaluation mode
- Scaler loading and feature ordering
- Feature matrix construction (50x6): T, H, P, G, delta, ratio
- Class mapping and softmax probability validation
- Independent per-node prediction execution
- End-to-end sensor data ingestion with rolling 5-hour window [C1..C5]
- Prediction persistence in database
- Farm-level disease state and localization activation
- Prediction retrieval APIs
"""
import pytest
import numpy as np
import torch
from datetime import datetime, timedelta, timezone

from app.ml.model import AttentionBiLSTM, Attention
from app.services.ml_service import (
    MLService,
    get_ml_service,
    CLASS_NAMES,
    DISEASE_CLASSES,
    HEALTHY_CLASSES
)
from app.models.sensor_cycle import SensorCycle
from app.models.farm import Farm
from app.models.node import Node
from app.models.prediction import Prediction
from app.core.config import settings
from tests.conftest import TestingSessionLocal, client


DEVICE_HEADERS = {"X-Device-API-Key": settings.DEVICE_API_KEY}


def test_model_architecture():
    """Verify Attention Bi-LSTM layer dimensions, forward pass output, and eval mode."""
    model = AttentionBiLSTM(
        input_dim=6,
        hidden_dim=128,
        num_layers=2,
        num_classes=5,
        dropout=0.3
    )
    model.eval()

    # Batch of 2, 50 time steps, 6 features
    dummy_input = torch.randn(2, 50, 6)
    with torch.no_grad():
        logits = model(dummy_input)

    assert logits.shape == (2, 5), f"Expected logits shape (2, 5), got {logits.shape}"
    assert not model.training, "Model should be in evaluation mode (model.eval())"


def test_attention_mechanism():
    """Verify attention weights sum to 1 across sequence length and produce context vector."""
    attn = Attention(hidden_dim=256)
    x = torch.randn(3, 50, 256)
    context, weights = attn(x)

    assert context.shape == (3, 256)
    assert weights.shape == (3, 50, 1)
    # Weights should sum to 1 over sequence dimension (dim=1)
    sum_weights = weights.sum(dim=1).squeeze(-1)
    np.testing.assert_allclose(sum_weights.detach().numpy(), np.ones(3), rtol=1e-5)


def test_scaler_and_ml_service_loading():
    """Verify MLService loads pre-trained state dictionary and pre-fitted scaler."""
    service = get_ml_service()
    assert service.model is not None
    assert service.scaler is not None
    assert not service.model.training

    # Check scaler handles 6 features without fitting
    sample_input = np.ones((50, 6), dtype=np.float64)
    scaled = service.scaler.transform(sample_input)
    assert scaled.shape == (50, 6)


def test_feature_matrix_construction():
    """
    Verify 50x6 matrix construction:
    Features: [T, H, P, Gas, Delta, Ratio]
    Delta: np.diff(gas_seq, prepend=gas_seq[0])
    Ratio: gas_seq / (gas_seq[0] + 1e-5)
    """
    service = get_ml_service()
    base_time = datetime(2026, 9, 12, 1, 0, tzinfo=timezone.utc)

    # Construct 5 synthetic cycles with distinct values
    cycles = []
    expected_gas_all = []
    for i in range(5):
        gas_vals = [float(10 * (i + 1) + j) for j in range(10)]
        expected_gas_all.extend(gas_vals)
        c = SensorCycle(
            cycle_id=i + 1,
            node_id="NODE_TEST",
            farm_id=1,
            cycle_timestamp=base_time + timedelta(hours=i),
            cycle_number=i + 1,
            gas_readings=gas_vals,
            temperature=20.0 + i,
            humidity=50.0 + i,
            pressure=1000.0 + i,
            is_valid=True
        )
        cycles.append(c)

    matrix = service.build_feature_matrix(cycles)
    assert matrix.shape == (50, 6), f"Expected shape (50, 6), got {matrix.shape}"

    expected_gas_seq = np.array(expected_gas_all, dtype=np.float64)
    expected_delta = np.diff(expected_gas_seq, prepend=expected_gas_seq[0])
    expected_ratio = expected_gas_seq / (expected_gas_seq[0] + 1e-5)

    # Verify each feature column
    # Column 0: Temperature (repeating for each cycle's 10 steps)
    for step in range(50):
        c_idx = step // 10
        assert matrix[step, 0] == cycles[c_idx].temperature
        assert matrix[step, 1] == cycles[c_idx].humidity
        assert matrix[step, 2] == cycles[c_idx].pressure

    # Column 3: Gas resistance
    np.testing.assert_allclose(matrix[:, 3], expected_gas_seq, rtol=1e-5)
    # Column 4: Delta
    np.testing.assert_allclose(matrix[:, 4], expected_delta, rtol=1e-5)
    # Column 5: Ratio
    np.testing.assert_allclose(matrix[:, 5], expected_ratio, rtol=1e-5)


def test_predict_output_structure_and_classes():
    """Verify inference output format, probability sum, and class names."""
    service = get_ml_service()
    base_time = datetime(2026, 9, 12, 1, 0, tzinfo=timezone.utc)

    cycles = [
        SensorCycle(
            cycle_id=i + 1,
            node_id="NODE_01",
            farm_id=1,
            cycle_timestamp=base_time + timedelta(hours=i),
            cycle_number=i + 1,
            gas_readings=[45.0 + j * 0.1 for j in range(10)],
            temperature=28.5,
            humidity=65.0,
            pressure=1010.0,
            is_valid=True
        )
        for i in range(5)
    ]

    result = service.predict(cycles, node_id="NODE_01", farm_id=1)

    assert result["node_id"] == "NODE_01"
    assert result["farm_id"] == 1
    assert result["predicted_class"] in CLASS_NAMES
    assert 0.0 <= result["confidence"] <= 1.0
    assert len(result["probabilities"]) == 5

    # Check exact class labels
    for c_name in CLASS_NAMES:
        assert c_name in result["probabilities"]

    # Softmax probabilities should sum to ~1.0
    prob_sum = sum(result["probabilities"].values())
    assert abs(prob_sum - 1.0) < 0.02, f"Probabilities sum to {prob_sum}, expected ~1.0"

    assert result["window_start"] == cycles[0].cycle_timestamp
    assert result["window_end"] == cycles[-1].cycle_timestamp
    assert result["cycle_ids"] == [1, 2, 3, 4, 5]


def test_independent_multi_node_prediction():
    """Verify that multiple nodes receive separate, independent predictions without concatenation."""
    service = get_ml_service()
    base_time = datetime(2026, 9, 12, 1, 0, tzinfo=timezone.utc)

    def make_cycles(node_id: str, offset: float):
        return [
            SensorCycle(
                cycle_id=i + 10,
                node_id=node_id,
                farm_id=1,
                cycle_timestamp=base_time + timedelta(hours=i),
                cycle_number=i + 1,
                gas_readings=[offset + j for j in range(10)],
                temperature=25.0 + offset,
                humidity=60.0,
                pressure=1012.0,
                is_valid=True
            )
            for i in range(5)
        ]

    cycles_n1 = make_cycles("NODE_01", 10.0)
    cycles_n2 = make_cycles("NODE_02", 50.0)
    cycles_n3 = make_cycles("NODE_03", 90.0)

    pred1 = service.predict(cycles_n1, "NODE_01", 1)
    pred2 = service.predict(cycles_n2, "NODE_02", 1)
    pred3 = service.predict(cycles_n3, "NODE_03", 1)

    assert pred1["node_id"] == "NODE_01"
    assert pred2["node_id"] == "NODE_02"
    assert pred3["node_id"] == "NODE_03"


ML_FARM_ID = 1


def ensure_ml_test_farm():
    global ML_FARM_ID
    # Register and login test farmer
    reg_payload = {
        "username": "ml_test_farmer",
        "email": "ml.farmer@bio-sniff.in",
        "password": "Password123!",
        "role": "farmer",
        "full_name": "ML Tester",
        "phone": "+91-9876543299",
        "state": "Punjab",
        "district": "Ludhiana"
    }
    client.post("/api/auth/register", json=reg_payload)
    login_resp = client.post("/api/auth/login", json={
        "username_or_email": "ml_test_farmer",
        "password": "Password123!"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    farm_payload = {
        "farm_name": "ML Pipeline Test Farm",
        "area": 25.0,
        "crop": "Rice (Paddy)",
        "crop_variety": "PR-126",
        "growth_stage": "Tillering",
        "latitude": 30.9010,
        "longitude": 75.8573,
        "status": "active"
    }
    farm_resp = client.post("/api/farms", json=farm_payload, headers=headers)
    ML_FARM_ID = farm_resp.json()["farm_id"]

    node_resp = client.post(
        "/api/nodes",
        json={
            "node_id": "NODE_ML_01",
            "farm_id": ML_FARM_ID,
            "node_name": "LSTM Probe 1",
            "latitude": 30.9015,
            "longitude": 75.8575,
            "is_master": False,
            "status": "online"
        },
        headers=headers
    )
    assert node_resp.status_code == 201
    return ML_FARM_ID


def test_full_pipeline_baseline_to_prediction():
    """
    Test end-to-end ingestion pipeline:
    - Ingest Cycles 1 to 4: prediction_ready=False, baseline collecting, no predictions
    - Ingest Cycle 5: prediction_ready=True, LSTM executes, prediction saved to DB
    - Ingest Cycle 6: rolling window slides to [C2..C6]
    """
    farm_id = ensure_ml_test_farm()

    base_time = datetime(2026, 9, 12, 10, 0, tzinfo=timezone.utc)

    # Ingest cycles 1..4 (Baseline period)
    for hour in range(4):
        payload = {
            "farm_id": farm_id,
            "timestamp": (base_time + timedelta(hours=hour)).isoformat(),
            "nodes": [
                {
                    "node_id": "NODE_ML_01",
                    "gas_resistance": [40.0 + i * 0.2 for i in range(10)],
                    "temperature": 27.0 + hour * 0.5,
                    "humidity": 65.0,
                    "pressure": 1011.0,
                    "battery": 95,
                    "signal": -65
                }
            ],
            "wind": {"average_speed": 2.1, "average_direction": 180.0}
        }
        res = client.post("/api/sensor-data", json=payload, headers=DEVICE_HEADERS)
        assert res.status_code == 200
        data = res.json()
        assert data["processed_nodes"][0]["prediction_ready"] is False
        assert data["processed_nodes"][0]["readiness_status"] == "collecting_baseline"
        assert len(data["predictions"]) == 0

    # Ingest Cycle 5 -> triggers prediction!
    payload_5 = {
        "farm_id": farm_id,
        "timestamp": (base_time + timedelta(hours=4)).isoformat(),
        "nodes": [
            {
                "node_id": "NODE_ML_01",
                "gas_resistance": [42.0 + i * 0.2 for i in range(10)],
                "temperature": 29.0,
                "humidity": 66.0,
                "pressure": 1010.5,
                "battery": 94,
                "signal": -64
            }
        ],
        "wind": {"average_speed": 2.5, "average_direction": 190.0}
    }
    res_5 = client.post("/api/sensor-data", json=payload_5, headers=DEVICE_HEADERS)
    assert res_5.status_code == 200
    data_5 = res_5.json()

    processed_node = data_5["processed_nodes"][0]
    assert processed_node["prediction_ready"] is True
    assert processed_node["readiness_status"] == "ready_for_prediction"
    assert len(data_5["predictions"]) == 1

    pred = data_5["predictions"][0]
    assert pred["node_id"] == "NODE_ML_01"
    assert pred["predicted_class"] in CLASS_NAMES
    assert pred["confidence"] > 0
    assert len(pred["probabilities"]) == 5
    assert len(pred["cycle_ids"]) == 5

    # Verify prediction persisted in DB
    db = TestingSessionLocal()
    db_pred = db.query(Prediction).filter(Prediction.node_id == "NODE_ML_01").first()
    assert db_pred is not None
    assert db_pred.predicted_class == pred["predicted_class"]
    assert db_pred.confidence == pred["confidence"]
    assert db_pred.window_start is not None
    assert db_pred.window_end is not None
    db.close()

    # Ingest Cycle 6 -> rolling window slides [C2..C6]
    payload_6 = {
        "farm_id": farm_id,
        "timestamp": (base_time + timedelta(hours=5)).isoformat(),
        "nodes": [
            {
                "node_id": "NODE_ML_01",
                "gas_resistance": [43.0 + i * 0.2 for i in range(10)],
                "temperature": 30.0,
                "humidity": 64.0,
                "pressure": 1009.5,
                "battery": 93,
                "signal": -65
            }
        ],
        "wind": {"average_speed": 3.0, "average_direction": 200.0}
    }
    res_6 = client.post("/api/sensor-data", json=payload_6, headers=DEVICE_HEADERS)
    assert res_6.status_code == 200
    data_6 = res_6.json()
    assert len(data_6["predictions"]) == 1
    cycle_ids_6 = data_6["predictions"][0]["cycle_ids"]
    assert len(cycle_ids_6) == 5
    # The first cycle (cycle 1) should no longer be in the latest 5-cycle window
    assert cycle_ids_6[0] != 1


def test_farm_predictions_api():
    """Verify GET /api/farms/{farm_id}/predictions and GET /api/nodes/{node_id}/predictions."""
    global ML_FARM_ID
    res_farm = client.get(f"/api/farms/{ML_FARM_ID}/predictions")
    assert res_farm.status_code == 200
    farm_pred_data = res_farm.json()
    assert farm_pred_data["farm_id"] == ML_FARM_ID
    assert "farm_disease_status" in farm_pred_data
    assert "localization_activated" in farm_pred_data
    assert len(farm_pred_data["predictions"]) >= 1

    res_node = client.get("/api/nodes/NODE_ML_01/predictions")
    assert res_node.status_code == 200
    node_preds = res_node.json()
    assert isinstance(node_preds, list)
    assert len(node_preds) >= 2
    assert node_preds[0]["node_id"] == "NODE_ML_01"

