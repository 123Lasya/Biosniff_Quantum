"""
Initializes and saves the prototype scaler_lstm.pkl and best_biosniff_lstm.pkl
if not already present on disk.
Preserves exact feature ordering and architecture:
Features (6):
1. Temperature
2. Humidity
3. Pressure
4. Gas resistance
5. Gas resistance difference
6. Gas resistance ratio
"""
import os
import torch
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib

from app.ml.model import AttentionBiLSTM

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCALER_PATH = os.path.join(BASE_DIR, "scaler_lstm.pkl")
MODEL_PATH = os.path.join(BASE_DIR, "best_biosniff_lstm.pkl")


def ensure_artifacts_exist():
    """Generates and persists prototype artifacts if missing."""
    os.makedirs(BASE_DIR, exist_ok=True)

    # 1. Scaler
    if not os.path.exists(SCALER_PATH):
        print(f"Generating prototype scaler at {SCALER_PATH}...")
        # Fit standard scaler on representative synthetic agricultural ranges
        np.random.seed(42)
        n_samples = 2000
        temps = np.random.normal(30.0, 4.0, (n_samples, 1))
        humids = np.random.normal(60.0, 10.0, (n_samples, 1))
        press = np.random.normal(1008.0, 5.0, (n_samples, 1))
        gas = np.random.normal(45.0, 10.0, (n_samples, 1))
        delta = np.random.normal(0.0, 1.5, (n_samples, 1))
        ratio = np.random.normal(1.0, 0.2, (n_samples, 1))

        synthetic_data = np.hstack([temps, humids, press, gas, delta, ratio])
        scaler = StandardScaler()
        scaler.fit(synthetic_data)
        joblib.dump(scaler, SCALER_PATH)
        print(f"Scaler successfully saved to {SCALER_PATH}")
    else:
        print(f"Scaler already exists at {SCALER_PATH}")

    # 2. Model State Dictionary
    if not os.path.exists(MODEL_PATH):
        print(f"Generating prototype model state dictionary at {MODEL_PATH}...")
        torch.manual_seed(42)
        model = AttentionBiLSTM(
            input_dim=6,
            hidden_dim=128,
            num_layers=2,
            num_classes=5,
            dropout=0.3
        )
        model.eval()
        # Save state dictionary as required by specification
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"Model state dictionary saved to {MODEL_PATH}")
    else:
        print(f"Model already exists at {MODEL_PATH}")


if __name__ == "__main__":
    ensure_artifacts_exist()
