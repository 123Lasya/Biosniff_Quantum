# BIO-SNIFF Backend API

Production-structured backend prototype for the **BIO-SNIFF Agricultural IoT System**.

BIO-SNIFF is an early crop disease detection and spatial localization network consisting of:
- **3 Sensor Nodes**: Each equipped with an e-nose gas sensor array (10 gas readings per cycle), ambient temperature, humidity, and barometric pressure.
- **Master ESP32 Gateway**: Aggregates hourly cycles from nodes, maintains connectivity via **5G cellular uplink** and local **Sub-GHz mesh**, and ingests telemetry into the backend.
- **FastAPI Core**: High-performance REST endpoints, JWT authentication for farmers/admins, and dedicated API-key hardware authentication for the Master ESP32 gateway.
- **SQLAlchemy 2.x & MySQL**: Authoritative spatial GPS coordinates, sensor cycles, LSTM predictions, and agronomic interventions.
- **Alembic Migrations**: Explicit and reproducible schema migration management.

---

## 1. Project Directory Structure

```text
backend/
├── alembic/
│   ├── env.py                  # Alembic environment linked to settings & Base.metadata
│   ├── script.py.mako          # Revision script template
│   └── versions/
│       └── 0001_initial_schema.py # Complete Bio-Sniff initial migration
├── alembic.ini                 # Alembic configuration
├── app/
│   ├── api/
│   │   ├── deps.py             # JWT bearer auth, user roles, device API-key verification
│   │   ├── routes/
│   │   │   ├── auth.py         # /api/auth/register, /api/auth/login, /api/auth/me
│   │   │   ├── farms.py        # /api/farms, /api/farms/{id}, /api/farms/{id}/nodes
│   │   │   ├── health.py       # /api/health
│   │   │   └── nodes.py        # /api/nodes, /api/nodes/{id}
│   │   └── __init__.py         # Consolidated API v1 router
│   ├── core/
│   │   ├── config.py           # Pydantic v2 BaseSettings, .env loader, CORS
│   │   ├── database.py         # SQLAlchemy 2.x engine, SessionLocal, Declarative Base
│   │   └── security.py         # Passlib bcrypt hashing, JWT encode/decode
│   ├── models/                 # SQLAlchemy 2.x Mapped models
│   │   ├── activity.py         # ActivityLog (audit trail)
│   │   ├── alert.py            # Alert (disease, missing node-data, battery)
│   │   ├── connectivity.py     # ConnectivityLog (5G RSSI/latency/packet loss)
│   │   ├── environment.py      # EnvironmentReading (wind, soil, ambient)
│   │   ├── farm.py             # Farm (authoritative coordinates, crops)
│   │   ├── farmer.py           # Farmer (profile)
│   │   ├── localization.py     # LocalizationResult (disease hotspot centroid)
│   │   ├── node.py             # Node (3-node capacity, GPS, mesh status)
│   │   ├── prediction.py       # Prediction (rolling 5h LSTM output)
│   │   ├── sensor_cycle.py     # SensorCycle (10 gas readings + temp/hum/press)
│   │   ├── user.py             # User (auth accounts, roles: FARMER, ADMIN)
│   │   └── __init__.py
│   ├── repositories/           # Data access repository layer
│   │   ├── farm_repo.py
│   │   ├── farmer_repo.py
│   │   ├── node_repo.py
│   │   └── user_repo.py
│   ├── schemas/                # Pydantic v2 schemas with ConfigDict
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── farm.py
│   │   ├── farmer.py
│   │   └── node.py
│   ├── services/               # Core business logic layer
│   │   ├── auth_service.py
│   │   ├── farm_service.py
│   │   └── node_service.py     # Enforces max 3 nodes per farm constraint
│   └── main.py                 # FastAPI application, CORS, lifespan handler
├── requirements.txt            # Python dependencies
├── .env.example                # Documented configuration template
├── .env                        # Local environment variables
└── tests/
    └── test_part1.py           # Automated test suite (health, auth, farms, nodes)
```

---

## 2. Environment Setup

### 2.1 Linux / macOS Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2.2 Local Windows Setup (PowerShell or Command Prompt)
1. **Prerequisites**: Ensure Python 3.11+ is installed with "Add Python to PATH" checked.
2. **Open PowerShell / Terminal** in the repository directory:
```powershell
cd backend
python -m venv venv
# Enable script execution if restricted:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
# (or in CMD: venv\Scripts\activate.bat)
```
3. **Install Dependencies**:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```
4. **Configure Environment File**:
```powershell
Copy-Item .env.example .env
# (or in CMD: copy .env.example .env)
```

Configuration parameters:

```env
PROJECT_NAME="Bio-Sniff Agricultural IoT Backend"
ENVIRONMENT="development"
API_V1_STR="/api"
SECRET_KEY="replace-with-a-very-secure-random-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DEVICE_API_KEY="biosniff-master-esp32-hw-key-secure"
# Use MySQL if installed, or SQLite for zero-setup local dev:
# DATABASE_URL="mysql+pymysql://biosniff_user:password@localhost:3306/biosniff_db"
DATABASE_URL="sqlite:///./biosniff.db"
CORS_ORIGINS="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
```

---

## 3. Database Migration & Seeding

### 3.1 Applying Alembic Migrations
To apply all database schema migrations:
```bash
# On Linux / macOS / Windows:
alembic upgrade head
```

### 3.2 Seeding Demo Data
To populate sample admin, regional farmers, farms, 3 nodes per farm, 24h cycle history, predictions, localization, alerts, and recommendations:
```bash
python ../scripts/seed_demo_data.py
```
Default demo accounts:
- **Admin**: `admin@biosniff.gov.in` / `Admin@123456`
- **Farmer**: `ramesh.patil@biosniff.com` / `Farmer@123456`

---

## 4. Running the Backend Server

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API documentation will be available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 5. Running Automated Tests

Run the complete test suite (Part 1 + Part 2) with pytest:

```bash
PYTHONPATH=. pytest tests/test_part1.py tests/test_part2.py -v
```

---

## 6. Part 2 — Hardware Ingestion Pipeline & Telemetry APIs

### 6.1 Overview & Ingestion Flow

The Master ESP32 Gateway transmits **one combined hourly payload** containing:
- `farm_id`: Identifies the target farm.
- `timestamp`: Hourly cycle timestamp in ISO-8601 format.
- `nodes`: List of up to 3 node cycles.
- `wind`: Microclimate wind measurements (`average_speed` in m/s >= 0, `average_direction` in degrees [0, 360]).

### 6.2 The Single Sensing Cycle Rule
- **10 Measurements = 1 Hour**: The ten gas resistance values represent the 10-step sensing cycle executed during that single hour. They do **not** represent ten hours.
- **Microclimate Ambient Conditions**: One temperature (°C), one relative humidity (%), and one barometric pressure (hPa) per node per hour.
- **Hardware Telemetry**: Node battery percentage (0-100%) and signal strength (RSSI dBm).

### 6.3 Partial-Success & Fault-Tolerant Ingestion
- **Malformed Node Rejection**: If one node submits a malformed gas array (e.g. < 10 values or non-numeric entries), valid nodes in the batch are saved to MySQL (`SensorCycle` table), the invalid node is rejected with a descriptive error reason, a validation alert is recorded in the `Alert` table, and the API returns `status: "partial_success"`.
- **Missing Registered Nodes**: If a node registered to the farm is absent from the batch payload, the backend **never fabricates data** and **never reuses prior cycles**. A `node_data_missing` alert is logged and the missing node is reported in `missing_nodes`.
- **Duplicate Cycle Prevention**: Re-submitting an identical timestamp for a node is detected and cleanly rejected without writing redundant records.

### 6.4 5-Hour Rolling Window & Prediction Readiness
- **Hours 1 to 4**:
  - Status: `collecting_baseline`
  - `prediction_ready: false`
  - `cycles_available: N`
  - `cycles_required: 5`
  - LSTM inference is **not** called.
- **Hour 5**:
  - Status: `ready_for_prediction`
  - `prediction_ready: true`
  - Latest window: `[C1, C2, C3, C4, C5]` (chronological order)
- **Hour 6 and Beyond**:
  - Window rolls dynamically to `[C2, C3, C4, C5, C6]`

### 6.5 Endpoints Summary

| Method | Route | Auth | Description |
|---|---|---|---|
| `POST` | `/api/sensor-data` | `X-Device-API-Key` | Ingests Master ESP32 hourly batch telemetry |
| `GET` | `/api/nodes/{node_id}/sensor-history` | Public / Dashboard | Node cycle history and rolling 5-hour window |
| `GET` | `/api/farms/{farm_id}/environment` | Public / Dashboard | Latest farm microclimate and node averages |
| `GET` | `/api/farms/{farm_id}/environment/history` | Public / Dashboard | Historical microclimate time-series (wind/temp/hum/press) |

### 6.6 Sample Payloads & Postman Collection
- Sample hourly payloads for Hours 1 through 6 are available in `backend/docs/sample_payloads.json`.
- A ready-to-import Postman collection is located in `backend/docs/BioSniff_Part2_Postman_Collection.json`.

---

## 7. Bio-Sniff Core Constraints & Architecture Rules

1. **Authoritative Node GPS**: Node latitude and longitude are stored directly in MySQL and are the single source of truth. No hardcoded coordinates.
2. **Farm Node Capacity**: Each farm strictly supports up to **3 sensor nodes** (`node_1`, `node_2`, `node_3`). Attempting to register a 4th node is rejected with `HTTP 400 Bad Request`.
3. **Master ESP32 Hardware Authentication**: Gateway telemetry ingestion uses the dedicated `X-Device-API-Key` header with `DEVICE_API_KEY`. User JWTs are **never** used for hardware nodes.
4. **Sensor Cycles & Hourly Ingestion**: Each sensor cycle stores an array of exactly **10 gas readings** alongside ambient temperature, humidity, and barometric pressure.
5. **Rolling 5-Hour LSTM Window**: Consecutive hourly cycles `[C1, C2, C3, C4, C5]` are fed to the disease classifier independently per node.
6. **Spatial Localization**: If even ONE node predicts disease, the farm status shifts to suspicious/disease-detected and spatial localization is activated without requiring consensus.

---

## 8. Part 3 — Attention Bi-LSTM ML Integration & Inference

### 8.1 Model Architecture & Specifications
The classification engine employs an **Attention Bidirectional LSTM** network (`AttentionBiLSTM`):
- **Input Dimension**: 6 features per time step
- **Hidden Dimension**: 128 (Bidirectional produces 256 concatenated output)
- **Number of Layers**: 2
- **Number of Classes**: 5
- **Dropout**: 0.3
- **Inference Mode**: CPU execution (`torch.device("cpu")`), strictly evaluated under `model.eval()` and `torch.no_grad()`.

### 8.2 The 50-Step Sequence & Deployment Adaptation
The trained ML model expects a sequence tensor of shape:
$$\text{batch} \times 50 \times 6$$

In the physical field hardware:
- Each node executes **1 cycle per hour** containing **10 gas resistance values**.
- The sliding 5-hour window collects 5 consecutive hourly cycles: $[C_1, C_2, C_3, C_4, C_5]$.
- Concatenating the gas readings in chronological sequence yields:
$$5 \text{ cycles} \times 10 \text{ values/cycle} = 50 \text{ sequence steps}$$
- Temperature, humidity, and barometric pressure for each cycle are matched to that cycle's 10 time steps.

### 8.3 The Six Feature Dimensions
For each time step $t \in [0, 49]$:
1. **Temperature** ($T$): Ambient temperature of the cycle (°C).
2. **Humidity** ($H$): Relative humidity of the cycle (%).
3. **Pressure** ($P$): Barometric pressure of the cycle (hPa).
4. **Gas Resistance** ($G$): Gas resistance measurement ($\text{k}\Omega$).
5. **Gas Resistance Difference** ($\Delta G$): First-order rate of change:
   $$\Delta G_t = \text{np.diff}(G, \text{prepend}=G_0)$$
6. **Gas Resistance Ratio** ($R$): Baseline normalization ratio:
   $$R_t = \frac{G_t}{G_0 + 10^{-5}}$$

### 8.4 Preprocessing & Scaling
- The input matrix $(50 \times 6)$ is transformed using the pre-trained `scaler_lstm.pkl` (`StandardScaler`).
- The scaler is **never refitted** during inference; only `scaler.transform(X)` is invoked.

### 8.5 Target Classes & Prediction Persistence
The model classifies volatile organic compound signatures into 5 target crop conditions:
- `0`: `Rice_Healthy`
- `1`: `Rice_Sheath_Blight`
- `2`: `Rice_Stem_Borer`
- `3`: `Jowar_Healthy`
- `4`: `Jowar_Shoot_Fly`

Softmax is applied to model logits to produce normalized probabilities:
- The predicted class is $\arg\max(P)$.
- The confidence score is $\max(P)$.
- If the predicted class is `Rice_Sheath_Blight`, `Rice_Stem_Borer`, or `Jowar_Shoot_Fly`:
  - `is_disease = True`
  - A critical alert (`crop_disease_detected`) is generated in the `Alert` repository.
  - The farm's status is set to `disease_detected`.
  - `localization_activated` is set to `True` for spatial tracking.

### 8.6 Prediction Retrieval Endpoints

| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/api/farms/{farm_id}/predictions` | JWT | Latest predictions for all farm nodes, overall disease status, localization activation flag |
| `GET` | `/api/nodes/{node_id}/predictions` | JWT | Historical prediction records and probability distributions for a specific node |

---

## 9. Part 4 — Wind-Aware Spatial Localization & Alerts

- **Spatial Plume Estimation**: Uses node geographic coordinates and Gaussian plume dispersion approximation based on wind velocity vector $(u, \theta)$ to localize disease origin $(x_0, y_0)$.
- **Confidence Radii & Hotspots**: Converts local Euclidean offsets to WGS-84 coordinates $(\text{lat}, \text{lng})$ with estimated confidence radius in meters.
- **Automated Agronomic Recommendations**: Maps identified pathogens (`Rice_Blast`, `Rice_Sheath_Blight`, `Rice_Stem_Borer`, etc.) to specific agrochemical treatments, organic interventions, and dosage guidelines.
- **Alert Dispatch**: Generates read/unread notifications for disease outbreaks, offline node states, and low-battery events.

---

## 10. Part 5 — Complete Production Backend APIs

### 10.1 Complete API Endpoint Reference

| Method | Route | Auth Header | Description |
|---|---|---|---|
| **Health** | | | |
| `GET` | `/api/health` | None | Service liveness, DB connection, uptime |
| **Authentication** | | | |
| `POST` | `/api/auth/register` | None | Register new farmer or admin account |
| `POST` | `/api/auth/login` | None | Authenticate and obtain JWT token |
| `GET` | `/api/auth/me` | `Authorization: Bearer <token>` | Get profile of currently logged-in user |
| **Farmer Dashboard & System** | | | |
| `GET` | `/api/farmer/dashboard/{farm_id}` | `Authorization: Bearer <token>` | Comprehensive farm overview: nodes, diseases, localization, weather, alerts |
| `GET` | `/api/farmer/system/{farm_id}` | `Authorization: Bearer <token>` | Detailed node hardware states, 5G uplink, battery telemetry, microclimate |
| **Admin Operations** | | | |
| `GET` | `/api/admin/dashboard` | `Authorization: Bearer <admin_token>` | Aggregated national farm statistics, network health, disease outbreaks |
| `GET` | `/api/admin/farms/map` | `Authorization: Bearer <admin_token>` | Geospatial points and health indicators for all farms across India |
| `GET` | `/api/admin/farmers` | `Authorization: Bearer <admin_token>` | Paginated, searchable directory of farmers with crop and health filters |
| `GET` | `/api/admin/farmers/{farmer_id}` | `Authorization: Bearer <admin_token>` | Full administrative profile for a specific farmer |
| **Farms & Management** | | | |
| `GET` | `/api/farms` | `Authorization: Bearer <token>` | List all farms belonging to the user (or all if admin) |
| `GET` | `/api/farms/{farm_id}` | `Authorization: Bearer <token>` | Farm details, crop stage, GPS coordinates, polygon boundary |
| `PUT` | `/api/farms/{farm_id}` | `Authorization: Bearer <token>` | Update farm configuration and metadata |
| `GET` | `/api/farms/{farm_id}/nodes` | `Authorization: Bearer <token>` | List all nodes deployed on this farm |
| **Nodes & Telemetry** | | | |
| `GET` | `/api/nodes` | `Authorization: Bearer <token>` | List all nodes |
| `GET` | `/api/nodes/{node_id}` | `Authorization: Bearer <token>` | Node details, firmware, battery, signal |
| `PUT` | `/api/nodes/{node_id}` | `Authorization: Bearer <token>` | Update node configuration (name, GPS coordinates) |
| `GET` | `/api/nodes/{node_id}/history` | `Authorization: Bearer <token>` | 24-hour cycle history with all 10 gas values, temp, humidity, pressure |
| `GET` | `/api/nodes/{node_id}/predictions` | `Authorization: Bearer <token>` | Historical ML predictions for this specific node |
| **Environment & 5G Connectivity** | | | |
| `GET` | `/api/farms/{farm_id}/environment` | `Authorization: Bearer <token>` | Current ambient conditions, wind vector, soil moisture |
| `GET` | `/api/farms/{farm_id}/environment/history` | `Authorization: Bearer <token>` | Time-series ambient microclimate for charting |
| `GET` | `/api/farms/{farm_id}/connectivity` | `Authorization: Bearer <token>` | Real-time 5G gateway status, latency, packet loss, RSSI |
| `GET` | `/api/farms/{farm_id}/connectivity/history`| `Authorization: Bearer <token>` | Historical network latency and connectivity logs |
| **Inference, Localization, Alerts & Recommendations** | | | |
| `POST` | `/api/sensor-data` | `X-Device-API-Key: <key>` | Ingest Master ESP32 hourly batch |
| `GET` | `/api/farms/{farm_id}/predictions` | `Authorization: Bearer <token>` | Recent predictions and disease status for farm |
| `GET` | `/api/farms/{farm_id}/localization/latest` | `Authorization: Bearer <token>` | Most recent wind-aware disease origin estimate and affected zone |
| `GET` | `/api/farms/{farm_id}/localization/history` | `Authorization: Bearer <token>` | Historical spatial localization records |
| `GET` | `/api/farms/{farm_id}/alerts` | `Authorization: Bearer <token>` | System and disease alerts for farm |
| `PUT` | `/api/alerts/{alert_id}/read` | `Authorization: Bearer <token>` | Mark alert as read (also supports PATCH) |
| `GET` | `/api/farms/{farm_id}/recommendations` | `Authorization: Bearer <token>` | Actionable treatment and dosage recommendations |

---

## 11. Master ESP32 Hardware Ingestion Guide

The Master ESP32 Gateway posts an hourly JSON payload to `POST /api/sensor-data`.

### Headers
```http
Content-Type: application/json
X-Device-API-Key: esp32-master-secret-key-99a8b7c6d5e4
```

### JSON Body Schema
```json
{
  "farm_id": 1,
  "timestamp": "2026-09-12T10:00:00Z",
  "wind": {
    "average_speed": 2.4,
    "average_direction": 48.0
  },
  "nodes": [
    {
      "node_id": "NODE_01",
      "temperature": 27.5,
      "humidity": 68.2,
      "pressure": 1008.4,
      "battery": 92.0,
      "signal": -72.0,
      "gas_resistance": [128.4, 131.2, 134.5, 136.0, 137.2, 138.1, 139.0, 140.2, 141.5, 142.0]
    },
    {
      "node_id": "NODE_02",
      "temperature": 27.2,
      "humidity": 69.1,
      "pressure": 1008.6,
      "battery": 88.0,
      "signal": -78.0,
      "gas_resistance": [210.0, 212.1, 214.5, 216.0, 217.2, 218.1, 219.0, 220.2, 221.5, 222.0]
    },
    {
      "node_id": "NODE_03",
      "temperature": 27.8,
      "humidity": 67.5,
      "pressure": 1008.2,
      "battery": 95.0,
      "signal": -69.0,
      "gas_resistance": [155.0, 157.1, 159.5, 161.0, 162.2, 163.1, 164.0, 165.2, 166.5, 167.0]
    }
  ]
}
```

---

## 12. Database Migrations & Seed Data

### 12.1 Applying Alembic Migrations
```bash
# Ensure MySQL or SQLite connection URL is set in .env or environment
alembic -c backend/alembic.ini upgrade head
```

### 12.2 Seeding Demo Data
To populate sample admin, farmers, farms, 3 nodes, 24h cycle history, predictions, localization, alerts, and recommendations:
```bash
python3 scripts/seed_demo_data.py
```
*Note: The seed script is completely idempotent and safe to run multiple times without duplicating or corrupting data.*

Default demo credentials:
- **Admin**: `admin@biosniff.gov.in` / `Admin@123456`
- **Farmer**: `ramesh.patil@biosniff.com` / `Farmer@123456`

---

## 13. Running Tests
To run all backend verification tests:
```bash
cd backend
PYTHONPATH=. pytest -v
```
