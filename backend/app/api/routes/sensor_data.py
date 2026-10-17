from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Security, Query, status, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import verify_device_api_key
from app.services.sensor_service import SensorDataService
from app.schemas.sensor_data import (
    MasterSensorPayload,
    SensorDataIngestResponse,
    NodeSensorHistoryResponse,
    FarmEnvironmentCurrentResponse,
    FarmEnvironmentHistoryResponse,
    FarmPredictionsResponse,
    NodePredictionResult,
)
from app.schemas.localization import (
    LocalizationResponse,
    FarmLocalizationHistoryResponse
)
from app.schemas.alert import (
    FarmAlertsResponse,
    NodeAlertsResponse,
    MarkAlertReadResponse
)

router = APIRouter(tags=["Hardware Ingestion & Telemetry"])


@router.post(
    "/sensor-data",
    response_model=SensorDataIngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest Master ESP32 Hourly Telemetry Payload",
    description=(
        "Hardware ingestion endpoint for the Master ESP32 Gateway. "
        "Requires dedicated X-Device-API-Key header. Ingests hourly cycles for up to 3 nodes, "
        "validates 10 gas values, updates rolling 5-hour window readiness, records microclimate wind, "
        "triggers wind-aware localization and recommendations on disease detection, "
        "handles partial-success when individual nodes are malformed, and creates alerts for missing nodes."
    )
)
def ingest_sensor_data(
    payload: MasterSensorPayload,
    api_key: str = Security(verify_device_api_key),
    db: Session = Depends(get_db)
) -> SensorDataIngestResponse:
    service = SensorDataService(db)
    return service.ingest_sensor_data(payload)


@router.api_route("/sensor-data/check-overdue", methods=["GET", "POST"], summary="Run hourly missing node check")
@router.api_route("/nodes/check-overdue", methods=["GET", "POST"], summary="Run hourly missing node check")
def check_overdue_nodes_sensor(
    farm_id: Optional[int] = Query(None, description="Optional farm_id to check"),
    db: Session = Depends(get_db)
):
    """
    Executes database-driven hourly missing node monitoring.
    Creates NODE_NO_DATA alerts for any nodes overdue for sensor ingestion.
    """
    service = SensorDataService(db)
    return service.check_overdue_nodes(farm_id_input=farm_id)


@router.get(
    "/nodes/{node_id}/sensor-history",
    response_model=NodeSensorHistoryResponse,
    summary="Get Node Sensor Cycle History and 5-Hour Rolling Window",
    description="Returns recent hourly cycles, latest 5-hour rolling window [C1..C5], and prediction readiness status for a node."
)
def get_node_sensor_history(
    node_id: str,
    limit: int = Query(50, ge=1, le=200, description="Max number of cycles to return"),
    only_valid: bool = Query(False, description="Filter to only valid cycles"),
    db: Session = Depends(get_db)
) -> NodeSensorHistoryResponse:
    service = SensorDataService(db)
    return service.get_node_sensor_history(node_id, limit=limit, only_valid=only_valid)


# ==========================================
# PART 4: LOCALIZATION, ALERTS & RECOMMENDATIONS
# ==========================================

@router.get(
    "/farms/{farm_id}/localization/latest",
    response_model=LocalizationResponse,
    summary="Get Latest Farm Disease Localization Result",
    description=(
        "Returns the most recent wind-aware source likelihood estimation and affected zone. "
        "If all nodes are healthy, returns active=false. Localization mathematics are performed in "
        "local metric coordinates and projected to geographic coordinates."
    )
)
def get_farm_localization_latest(
    farm_id: int,
    db: Session = Depends(get_db)
) -> LocalizationResponse:
    service = SensorDataService(db)
    return service.get_farm_localization_latest(farm_id)


@router.get(
    "/farms/{farm_id}/localization/history",
    response_model=FarmLocalizationHistoryResponse,
    summary="Get Farm Localization History",
    description="Returns historical localization events with source coordinates, affected zones, and likelihood scores."
)
def get_farm_localization_history(
    farm_id: int,
    limit: int = Query(50, ge=1, le=200, description="Max number of localization events to return"),
    db: Session = Depends(get_db)
) -> FarmLocalizationHistoryResponse:
    service = SensorDataService(db)
    return service.get_farm_localization_history(farm_id, limit=limit)


@router.get(
    "/farms/{farm_id}/alerts",
    response_model=FarmAlertsResponse,
    summary="Get Farm System & Disease Alerts",
    description="Returns all active and historical alerts for a farm, including DISEASE_ALERT, NODE_NO_DATA, LOW_BATTERY, etc."
)
def get_farm_alerts(
    farm_id: int,
    limit: int = Query(50, ge=1, le=200, description="Max number of alerts to return"),
    db: Session = Depends(get_db)
) -> FarmAlertsResponse:
    service = SensorDataService(db)
    return service.get_farm_alerts(farm_id, limit=limit)


@router.get(
    "/nodes/{node_id}/alerts",
    response_model=NodeAlertsResponse,
    summary="Get Node-Specific Alerts",
    description="Returns alerts for a specific hardware node (e.g. LOW_BATTERY, NODE_NO_DATA, CONNECTIVITY_WARNING)."
)
def get_node_alerts(
    node_id: str,
    limit: int = Query(50, ge=1, le=200, description="Max number of alerts to return"),
    db: Session = Depends(get_db)
) -> NodeAlertsResponse:
    service = SensorDataService(db)
    return service.get_node_alerts(node_id, limit=limit)


@router.put(
    "/alerts/{alert_id}/read",
    response_model=MarkAlertReadResponse,
    summary="Mark Alert as Read (PUT)",
    description="Updates the read status of an alert."
)
def mark_alert_read_put(
    alert_id: int = Path(..., description="ID of the alert to mark as read"),
    db: Session = Depends(get_db)
) -> MarkAlertReadResponse:
    service = SensorDataService(db)
    return service.mark_alert_read(alert_id)


@router.patch(
    "/alerts/{alert_id}/read",
    response_model=MarkAlertReadResponse,
    summary="Mark Alert as Read (PATCH)",
    description="Updates the read status of an alert."
)
def mark_alert_read_patch(
    alert_id: int = Path(..., description="ID of the alert to mark as read"),
    db: Session = Depends(get_db)
) -> MarkAlertReadResponse:
    service = SensorDataService(db)
    return service.mark_alert_read(alert_id)


@router.get(
    "/farms/{farm_id}/recommendations",
    summary="Get Farm Agronomic Recommendations",
    description="Returns agronomic treatment and management recommendations tailored to current or past detected conditions."
)
def get_farm_recommendations(
    farm_id: int,
    limit: int = Query(50, ge=1, le=200, description="Max recommendations to return"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    service = SensorDataService(db)
    return service.get_farm_recommendations(farm_id, limit=limit)


