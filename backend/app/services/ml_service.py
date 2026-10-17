"""
Bio-Sniff ML Inference Service.
Loads the Attention Bi-LSTM model and StandardScaler.
Constructs the 50x6 feature sequence across the rolling 5-hour window,
runs inference independently per node, and computes class probabilities via softmax.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import numpy as np
import joblib
import torch
import torch.nn.functional as F

from app.ml.model import AttentionBiLSTM
from app.models.sensor_cycle import SensorCycle

logger = logging.getLogger("biosniff.ml_service")

# Exact class order from training specification
CLASS_NAMES = [
    "Rice_Healthy",
    "Rice_Sheath_Blight",
    "Rice_Stem_Borer",
    "Jowar_Healthy",
    "Jowar_Shoot_Fly"
]

DISEASE_CLASSES = {
    "Rice_Sheath_Blight",
    "Rice_Stem_Borer",
    "Jowar_Shoot_Fly"
}

HEALTHY_CLASSES = {
    "Rice_Healthy",
    "Jowar_Healthy"
}

DEFAULT_MODEL_VERSION = "biosniff-attention-bilstm-v1-prototype"


class MLService:
    def __init__(
        self,
        model_path: Optional[str] = None,
        scaler_path: Optional[str] = None,
        device: str = "cpu"
    ):
        self.device = torch.device(device)
        self.model_version = DEFAULT_MODEL_VERSION

        # Resolve paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_ml_dir = os.path.join(base_dir, "ml")
        
        self.scaler_path = scaler_path or os.path.join(default_ml_dir, "scaler_lstm.pkl")
        self.model_path = model_path or os.path.join(default_ml_dir, "best_biosniff_lstm.pkl")

        # Load scaler and model
        self.scaler = self._load_scaler(self.scaler_path)
        self.model = self._load_model(self.model_path)

    def _load_scaler(self, path: str):
        """Loads the pre-fitted StandardScaler. Does NOT refit during inference."""
        if not os.path.exists(path):
            from app.ml.init_prototype_artifacts import ensure_artifacts_exist
            logger.warning(f"Scaler not found at {path}. Generating prototype scaler...")
            ensure_artifacts_exist()

        logger.info(f"Loading scaler from {path}")
        scaler = joblib.load(path)
        return scaler

    def _load_model(self, path: str) -> AttentionBiLSTM:
        """
        Recreates the Attention Bi-LSTM architecture and loads the saved state dictionary.
        Sets model to eval() mode on the specified device.
        """
        if not os.path.exists(path):
            from app.ml.init_prototype_artifacts import ensure_artifacts_exist
            logger.warning(f"Model weights not found at {path}. Generating prototype weights...")
            ensure_artifacts_exist()

        logger.info(f"Recreating AttentionBiLSTM (input=6, hidden=128, layers=2, classes=5, dropout=0.3)")
        model = AttentionBiLSTM(
            input_dim=6,
            hidden_dim=128,
            num_layers=2,
            num_classes=5,
            dropout=0.3
        )

        logger.info(f"Loading model state dictionary from {path}")
        state_dict = torch.load(path, map_location=self.device)
        model.load_state_dict(state_dict)
        model.to(self.device)
        model.eval()
        return model

    def build_feature_matrix(self, cycles: List[SensorCycle]) -> np.ndarray:
        """
        Constructs the (50, 6) feature matrix from a node's 5 chronological hourly cycles.

        Window layout:
        - 5 cycles [C1, C2, C3, C4, C5] sorted chronologically
        - Each cycle contains exactly 10 gas values -> 50 sequence steps total.
        - gas_seq = flattened 50 gas values
        - gas_delta = np.diff(gas_seq, prepend=gas_seq[0])
        - gas_ratio = gas_seq / (gas_seq[0] + 1e-5)

        Deployment adaptation for Environmental T/H/P:
        - Each hourly cycle's physical T, H, P is assigned to its respective 10 steps:
          steps 0..9 -> C1 ambient, steps 10..19 -> C2 ambient, ..., steps 40..49 -> C5 ambient.
        - Features order (matches scaler training order):
          [Temperature, Humidity, Pressure, Gas resistance, Gas difference, Gas ratio]
        """
        if len(cycles) != 5:
            raise ValueError(f"MLService requires exactly 5 cycles for inference, received {len(cycles)}")

        # Ensure cycles are in chronological order
        sorted_cycles = sorted(cycles, key=lambda c: c.cycle_timestamp)

        # 1. Flatten gas values across the 5 cycles
        gas_seq_list = []
        for c in sorted_cycles:
            readings = c.gas_readings
            if not isinstance(readings, list) or len(readings) != 10:
                raise ValueError(f"Cycle {c.cycle_id} does not contain exactly 10 gas readings")
            gas_seq_list.extend([float(v) for v in readings])

        gas_seq = np.array(gas_seq_list, dtype=np.float64)  # (50,)

        # 2. Compute gas delta and ratio exactly as specified in training code
        gas_delta = np.diff(gas_seq, prepend=gas_seq[0])
        gas_ratio = gas_seq / (gas_seq[0] + 1e-5)

        # 3. Build the 50x6 matrix
        # Columns: [T, H, P, G, D, R]
        matrix = np.zeros((50, 6), dtype=np.float64)

        for step in range(50):
            cycle_idx = step // 10
            c = sorted_cycles[cycle_idx]
            matrix[step, 0] = float(c.temperature)
            matrix[step, 1] = float(c.humidity)
            matrix[step, 2] = float(c.pressure)
            matrix[step, 3] = gas_seq[step]
            matrix[step, 4] = gas_delta[step]
            matrix[step, 5] = gas_ratio[step]

        return matrix

    def predict(self, cycles: List[SensorCycle], node_id: str, farm_id: int) -> Dict[str, Any]:
        """
        Runs independent LSTM inference on a node's 5-cycle window.
        Returns predicted class, confidence, softmax probabilities, and window boundaries.
        """
        if len(cycles) != 5:
            raise ValueError(f"Cannot run prediction: expected 5 cycles for node {node_id}, got {len(cycles)}")

        sorted_cycles = sorted(cycles, key=lambda c: c.cycle_timestamp)
        window_start = sorted_cycles[0].cycle_timestamp
        window_end = sorted_cycles[-1].cycle_timestamp
        cycle_ids = [c.cycle_id for c in sorted_cycles]

        # 1. Construct raw 50x6 feature matrix
        raw_matrix = self.build_feature_matrix(sorted_cycles)

        # 2. Transform using pre-loaded StandardScaler (no refitting!)
        scaled_matrix = self.scaler.transform(raw_matrix)  # (50, 6)

        # 3. Convert to PyTorch Tensor of shape (1, 50, 6)
        tensor = torch.tensor(scaled_matrix, dtype=torch.float32).unsqueeze(0).to(self.device)

        # 4. Model Inference
        with torch.no_grad():
            logits = self.model(tensor)  # (1, 5)
            probabilities = F.softmax(logits, dim=1).squeeze(0).cpu().numpy()

        # 5. Extract prediction & probabilities
        pred_idx = int(np.argmax(probabilities))
        predicted_class = CLASS_NAMES[pred_idx]
        confidence = float(probabilities[pred_idx])

        # Map all 5 classes with their exact labels
        prob_dict = {
            CLASS_NAMES[i]: float(round(float(probabilities[i]), 4))
            for i in range(len(CLASS_NAMES))
        }

        is_disease = predicted_class in DISEASE_CLASSES

        return {
            "node_id": node_id,
            "farm_id": farm_id,
            "predicted_class": predicted_class,
            "is_disease": is_disease,
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "window_start": window_start,
            "window_end": window_end,
            "cycle_ids": cycle_ids,
            "latest_cycle_id": sorted_cycles[-1].cycle_id,
            "model_version": self.model_version
        }


# Singleton instance
_ml_service_instance: Optional[MLService] = None


def get_ml_service() -> MLService:
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLService()
    return _ml_service_instance
