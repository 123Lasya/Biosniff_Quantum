import math
import re
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.farm import Farm
from app.models.node import Node
from app.models.sensor_cycle import SensorCycle
from app.repositories.farm_repo import FarmRepository
from app.repositories.node_repo import NodeRepository
from app.repositories.sensor_cycle_repo import SensorCycleRepository
from app.repositories.environment_repo import EnvironmentRepository
from app.repositories.alert_repo import AlertRepository
from app.repositories.prediction_repo import PredictionRepository
from app.repositories.localization_repo import LocalizationRepository
from app.repositories.recommendation_repo import RecommendationRepository
from app.services.ml_service import get_ml_service
from app.services.localization_service import LocalizationService
from app.services.recommendation_service import RecommendationService
from app.services.alert_service import AlertService, AlertType
from app.schemas.sensor_data import (
    MasterSensorPayload,
    NodeCyclePayload,
    SensorDataIngestResponse,
    ProcessedNodeResult,
    RejectedNodeResult,
    MissingNodeResult,
    NodePredictionResult,
    NodeSensorHistoryResponse,
    SensorCycleItem,
    FarmEnvironmentCurrentResponse,
    FarmEnvironmentHistoryResponse,
    FarmPredictionsResponse,
    EnvironmentReadingItem
)
from app.schemas.localization import (
    LocalizationResponse,
    FarmLocalizationHistoryResponse,
    LocalizationHistoryItem,
    LocalCoordinate,
    GeoCoordinate,
    AffectedZone
)
from app.schemas.alert import (
    AlertItem,
    FarmAlertsResponse,
    NodeAlertsResponse,
    MarkAlertReadResponse
)


class SensorDataService:
    def __init__(self, db: Session):
        self.db = db
        self.farm_repo = FarmRepository(db)
        self.node_repo = NodeRepository(db)
        self.sensor_cycle_repo = SensorCycleRepository(db)
        self.environment_repo = EnvironmentRepository(db)
        self.alert_repo = AlertRepository(db)
        self.prediction_repo = PredictionRepository(db)
        self.localization_repo = LocalizationRepository(db)
        self.recommendation_repo = RecommendationRepository(db)
        self.ml_service = get_ml_service()
        self.localization_service = LocalizationService(db)
        self.recommendation_service = RecommendationService(db)
        self.alert_service = AlertService(db)

    def resolve_farm(self, farm_id_input: Union[int, str]) -> Optional[Farm]:
        """
        Resolves a farm by integer ID, string ID ('1', 'FARM_001'), or farm name.
        """
        if isinstance(farm_id_input, int):
            return self.farm_repo.get_by_id(farm_id_input)
        
        farm_str = str(farm_id_input).strip()
        if farm_str.isdigit():
            farm = self.farm_repo.get_by_id(int(farm_str))
            if farm:
                return farm

        # Try extracting digits if format like "FARM_001" or "FARM_1"
        digits = re.findall(r'\d+', farm_str)
        if digits:
            candidate_id = int(digits[0])
            farm = self.farm_repo.get_by_id(candidate_id)
            if farm:
                return farm

        # Try by farm name match
        farm = self.db.query(Farm).filter(Farm.farm_name == farm_str).first()
        if farm:
            return farm

        return None

    def resolve_node(self, node_id_input: str, farm_id: int) -> Optional[Node]:
        """
        Resolves a hardware node by exact ID or case/formatting normalization (NODE_01 <-> node_1).
        """
        # Exact match
        node = self.node_repo.get_by_id(node_id_input)
        if node:
            return node

        # Case-insensitive match
        node = self.db.query(Node).filter(
            func.lower(Node.node_id) == node_id_input.lower()
        ).first()
        if node:
            return node

        # Normalized match (e.g. NODE_01 -> node_1, node1)
        normalized = node_id_input.lower().replace("-", "_")
        m = re.match(r'node_?0*(\d+)', normalized)
        if m:
            num = m.group(1)
            candidates = [f"node_{num}", f"node{num}", f"NODE_{num}", f"node_0{num}", f"NODE_0{num}"]
            for c in candidates:
                node = self.node_repo.get_by_id(c)
                if node:
                    return node

        return None

    def validate_node_cycle(
        self,
        node_payload: NodeCyclePayload,
        farm: Farm
    ) -> tuple[Optional[Node], Optional[List[float]], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[str]]:
        """
        Validates individual node cycle telemetry:
        - node exists and belongs to farm
        - exactly 10 gas values, all numeric
        - temperature, humidity, pressure are numeric
        - battery (if supplied) between 0 and 100
        - signal (if supplied) is numeric
        Returns: (node, gas_readings, temp, hum, press, battery, signal, error_reason)
        """
        node = self.resolve_node(node_payload.node_id, farm.farm_id)
        if not node:
            return None, None, None, None, None, None, None, f"Node '{node_payload.node_id}' is not registered in the system"

        if node.farm_id != farm.farm_id:
            return None, None, None, None, None, None, None, f"Node '{node.node_id}' is registered to farm_id={node.farm_id}, not {farm.farm_id}"

        # Validate gas resistance
        gas_raw = node_payload.gas_resistance
        if not isinstance(gas_raw, (list, tuple)):
            return node, None, None, None, None, None, None, f"gas_resistance must be an array of exactly 10 numeric values, got {type(gas_raw).__name__}"

        if len(gas_raw) != 10:
            return node, None, None, None, None, None, None, f"Invalid gas resistance array: expected 10 values, got {len(gas_raw)}"

        cleaned_gas: List[float] = []
        for idx, val in enumerate(gas_raw):
            if val is None or isinstance(val, bool) or not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                return node, None, None, None, None, None, None, f"gas_resistance index {idx} has invalid non-numeric value: {val}"
            cleaned_gas.append(float(val))

        # Validate temperature
        try:
            if node_payload.temperature is None or isinstance(node_payload.temperature, bool):
                raise ValueError()
            temp = float(node_payload.temperature)
            if math.isnan(temp) or math.isinf(temp):
                raise ValueError()
        except (ValueError, TypeError):
            return node, None, None, None, None, None, None, f"Invalid temperature value: {node_payload.temperature}"

        # Validate humidity
        try:
            if node_payload.humidity is None or isinstance(node_payload.humidity, bool):
                raise ValueError()
            hum = float(node_payload.humidity)
            if math.isnan(hum) or math.isinf(hum):
                raise ValueError()
        except (ValueError, TypeError):
            return node, None, None, None, None, None, None, f"Invalid humidity value: {node_payload.humidity}"

        # Validate pressure
        try:
            if node_payload.pressure is None or isinstance(node_payload.pressure, bool):
                raise ValueError()
            press = float(node_payload.pressure)
            if math.isnan(press) or math.isinf(press):
                raise ValueError()
        except (ValueError, TypeError):
            return node, None, None, None, None, None, None, f"Invalid pressure value: {node_payload.pressure}"

        # Validate battery (optional)
        battery: Optional[float] = None
        if node_payload.battery is not None:
            try:
                if isinstance(node_payload.battery, bool):
                    raise ValueError()
                b_val = float(node_payload.battery)
                if math.isnan(b_val) or b_val < 0.0 or b_val > 100.0:
                    return node, None, None, None, None, None, None, f"Battery percentage must be between 0 and 100, got {node_payload.battery}"
                battery = b_val
            except (ValueError, TypeError):
                return node, None, None, None, None, None, None, f"Battery percentage must be numeric between 0 and 100, got {node_payload.battery}"

        # Validate signal (optional)
        signal: Optional[float] = None
        if node_payload.signal is not None:
            try:
                if isinstance(node_payload.signal, bool):
                    raise ValueError()
                s_val = float(node_payload.signal)
                if math.isnan(s_val) or math.isinf(s_val):
                    raise ValueError()
                signal = s_val
            except (ValueError, TypeError):
                return node, None, None, None, None, None, None, f"Signal strength must be numeric, got {node_payload.signal}"

        return node, cleaned_gas, temp, hum, press, battery, signal, None

    def ingest_sensor_data(self, payload: MasterSensorPayload) -> SensorDataIngestResponse:
        """
        Main ingestion entry point for Master ESP32 Gateway hourly payloads.
        Executes:
        - Farm verification
        - Wind microclimate validation
        - Individual node validation and duplicate detection
        - Partial success handling (saving valid nodes, alerting on invalid ones)
        - Missing node detection (for registered nodes absent in the batch)
        - 5-hour rolling window readiness calculation
        - Environmental data storage
        """
        # 1. Resolve Farm
        farm = self.resolve_farm(payload.farm_id)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{payload.farm_id}' was not found in system records"
            )

        # 2. Validate Wind parameters if provided
        wind_speed = 0.0
        wind_dir_str: Optional[str] = None
        wind_dir_deg: Optional[float] = None
        if payload.wind is not None:
            if payload.wind.average_speed < 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Wind average_speed must be non-negative (>= 0)"
                )
            if payload.wind.average_direction < 0 or payload.wind.average_direction > 360:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Wind average_direction must be within [0, 360] degrees"
                )
            wind_speed = float(payload.wind.average_speed)
            wind_dir_deg = float(payload.wind.average_direction)
            wind_dir_str = str(payload.wind.average_direction)

        # 3. Retrieve all currently registered nodes for this farm
        registered_nodes = self.node_repo.get_by_farm_id(farm.farm_id)
        registered_node_ids = {n.node_id for n in registered_nodes}

        processed_nodes: List[ProcessedNodeResult] = []
        rejected_nodes: List[RejectedNodeResult] = []
        seen_node_ids_in_batch: set = set()

        batch_predictions: List[NodePredictionResult] = []
        disease_detected_in_batch = False
        batch_alerts: List[Dict[str, Any]] = []

        valid_temps: List[float] = []
        valid_hums: List[float] = []
        valid_press: List[float] = []

        # 4. Process each node cycle in the payload
        for n_payload in payload.nodes:
            raw_node_id = n_payload.node_id
            
            # Individual node validation
            node, gas_readings, temp, hum, press, battery, signal, error = self.validate_node_cycle(
                n_payload, farm
            )

            if error:
                # Malformed or unauthorized node: reject and create validation alert
                rejected_nodes.append(RejectedNodeResult(
                    node_id=raw_node_id,
                    status="rejected",
                    reason=error
                ))
                val_alert = self.alert_service.create_alert(
                    farm_id=farm.farm_id,
                    node_id=node.node_id if node else None,
                    alert_type=AlertType.SENSOR_DATA_ERROR.value,
                    severity="warning",
                    title=f"Telemetry Validation Error on Node {raw_node_id}",
                    message=f"Node {raw_node_id} submitted invalid hourly cycle: {error}"
                )
                batch_alerts.append(self.alert_service._format_alert(val_alert))
                continue

            node_actual_id = node.node_id
            seen_node_ids_in_batch.add(node_actual_id)

            # Duplicate hourly batch detection for this node
            if self.sensor_cycle_repo.is_duplicate(node_actual_id, farm.farm_id, payload.timestamp):
                rejected_nodes.append(RejectedNodeResult(
                    node_id=node_actual_id,
                    status="rejected",
                    reason=f"Duplicate hourly cycle detected for node '{node_actual_id}' at timestamp {payload.timestamp.isoformat()}"
                ))
                dup_alert = self.alert_service.create_alert(
                    farm_id=farm.farm_id,
                    node_id=node_actual_id,
                    alert_type=AlertType.SENSOR_DATA_ERROR.value,
                    severity="info",
                    title=f"Duplicate Hourly Cycle Ignored for {node_actual_id}",
                    message=f"A cycle for node {node_actual_id} at {payload.timestamp} has already been ingested. Duplicate record omitted."
                )
                batch_alerts.append(self.alert_service._format_alert(dup_alert))
                continue

            # Check for low battery warning
            if battery is not None and battery < 20.0:
                bat_alert = self.alert_service.create_alert(
                    farm_id=farm.farm_id,
                    node_id=node_actual_id,
                    alert_type=AlertType.LOW_BATTERY.value,
                    severity="warning",
                    title=f"Low Battery on Node {node_actual_id}",
                    message=f"Hardware node {node_actual_id} reported battery level of {battery:.1f}%."
                )
                batch_alerts.append(self.alert_service._format_alert(bat_alert))

            # Check for weak connectivity warning (RSSI < -85 dBm)
            if signal is not None and signal < -85.0:
                conn_alert = self.alert_service.create_alert(
                    farm_id=farm.farm_id,
                    node_id=node_actual_id,
                    alert_type=AlertType.CONNECTIVITY_WARNING.value,
                    severity="warning",
                    title=f"Weak Connectivity on Node {node_actual_id}",
                    message=f"Hardware node {node_actual_id} reported weak signal strength ({signal} dBm < -85 dBm threshold)."
                )
                batch_alerts.append(self.alert_service._format_alert(conn_alert))

            # Save valid sensor cycle
            db_cycle = self.sensor_cycle_repo.create(
                node_id=node_actual_id,
                farm_id=farm.farm_id,
                cycle_timestamp=payload.timestamp,
                gas_readings=gas_readings,
                temperature=temp,
                humidity=hum,
                pressure=press,
                battery=battery,
                signal=signal,
                is_valid=True,
                raw_payload=n_payload.model_dump()
            )

            # Update hardware node telemetry
            self.node_repo.update_telemetry(
                node=node,
                battery_percentage=battery,
                signal_strength=signal,
                status="online"
            )

            # Accumulate for farm-level environmental microclimate
            valid_temps.append(temp)
            valid_hums.append(hum)
            valid_press.append(press)

            # 5-Hour Sliding Window & Prediction Readiness Calculation
            # Count total valid cycles for this node
            total_valid = self.sensor_cycle_repo.count_valid_cycles(node_actual_id)
            prediction_ready = total_valid >= 5
            readiness_status = "ready_for_prediction" if prediction_ready else "collecting_baseline"
            latest_window = self.sensor_cycle_repo.get_latest_valid_window(node_actual_id, window_size=5)
            latest_5_ids = [c.cycle_id for c in latest_window] if prediction_ready else []

            node_prediction_obj: Optional[NodePredictionResult] = None

            # Execute model inference independently per eligible node
            if prediction_ready and len(latest_window) == 5:
                pred_dict = self.ml_service.predict(
                    cycles=latest_window,
                    node_id=node_actual_id,
                    farm_id=farm.farm_id
                )

                # Persist prediction in predictions database table
                pred_db = self.prediction_repo.create(
                    node_id=node_actual_id,
                    farm_id=farm.farm_id,
                    cycle_id=db_cycle.cycle_id,
                    window_cycle_ids=latest_5_ids,
                    predicted_class=pred_dict["predicted_class"],
                    disease_detected=pred_dict["is_disease"],
                    confidence=pred_dict["confidence"],
                    all_class_probabilities=pred_dict["probabilities"],
                    model_version=pred_dict["model_version"],
                    window_start=pred_dict["window_start"],
                    window_end=pred_dict["window_end"]
                )

                node_prediction_obj = NodePredictionResult(
                    prediction_id=pred_db.prediction_id,
                    node_id=node_actual_id,
                    farm_id=farm.farm_id,
                    predicted_class=pred_dict["predicted_class"],
                    is_disease=pred_dict["is_disease"],
                    confidence=pred_dict["confidence"],
                    probabilities=pred_dict["probabilities"],
                    window_start=pred_dict["window_start"],
                    window_end=pred_dict["window_end"],
                    model_version=pred_dict["model_version"],
                    cycle_ids=latest_5_ids
                )
                batch_predictions.append(node_prediction_obj)

                if pred_dict["is_disease"]:
                    disease_detected_in_batch = True
                    node_severity = "critical" if pred_dict["confidence"] >= 0.85 else "warning"
                    # Create alert for detected crop disease on this node
                    dis_alert = self.alert_service.create_alert(
                        farm_id=farm.farm_id,
                        node_id=node_actual_id,
                        alert_type=AlertType.DISEASE_ALERT.value,
                        severity=node_severity,
                        title=f"Crop Disease Detected on Node {node_actual_id}: {pred_dict['predicted_class']}",
                        message=(
                            f"Attention Bi-LSTM model classified {pred_dict['predicted_class']} "
                            f"with {pred_dict['confidence'] * 100:.1f}% confidence for node {node_actual_id}."
                        )
                    )
                    batch_alerts.append(self.alert_service._format_alert(dis_alert))

            processed_nodes.append(ProcessedNodeResult(
                node_id=node_actual_id,
                status="saved",
                cycle_id=db_cycle.cycle_id,
                cycle_number=db_cycle.cycle_number,
                prediction_ready=prediction_ready,
                readiness_status=readiness_status,
                cycles_available=total_valid,
                cycles_required=5,
                latest_5_cycle_ids=latest_5_ids,
                prediction=node_prediction_obj
            ))

        # 5. Missing node detection (registered nodes that did not report in this batch)
        missing_nodes: List[MissingNodeResult] = []
        for reg_node in registered_nodes:
            if reg_node.node_id not in seen_node_ids_in_batch:
                # Do NOT fabricate or reuse previous cycle
                # Create NODE_NO_DATA alert for missing telemetry
                mis_alert = self.alert_service.create_alert(
                    farm_id=farm.farm_id,
                    node_id=reg_node.node_id,
                    alert_type=AlertType.NODE_NO_DATA.value,
                    severity="warning",
                    title=f"Node {reg_node.node_id} Missing in Hourly Ingestion",
                    message=f"Node '{reg_node.node_id}' ({reg_node.node_name}) did not submit telemetry for hourly cycle at {payload.timestamp.isoformat()}."
                )
                batch_alerts.append(self.alert_service._format_alert(mis_alert))
                missing_nodes.append(MissingNodeResult(
                    node_id=reg_node.node_id,
                    status="missing_in_batch",
                    alert_created=True,
                    message=f"Node {reg_node.node_id} was absent from the batch payload; missing cycle alert created."
                ))

        # 6. Store Environment Data (Wind + average T/H/P)
        env_saved = False
        if payload.wind is not None or valid_temps:
            avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else 25.0
            avg_hum = sum(valid_hums) / len(valid_hums) if valid_hums else 50.0
            avg_press = sum(valid_press) / len(valid_press) if valid_press else 1013.25

            self.environment_repo.create(
                farm_id=farm.farm_id,
                recorded_at=payload.timestamp,
                wind_speed=wind_speed,
                wind_direction=wind_dir_str,
                ambient_temp=round(avg_temp, 2),
                humidity=round(avg_hum, 2),
                pressure=round(avg_press, 2)
            )
            env_saved = True

        # 7. Collect Detected Conditions & Prepare Localization Inputs
        all_node_prediction_inputs = []
        pred_by_node = {p.node_id: p for p in batch_predictions}

        # Query all registered nodes for the farm to pass actual MySQL coordinates
        for reg_node in registered_nodes:
            p = pred_by_node.get(reg_node.node_id)
            if p:
                all_node_prediction_inputs.append({
                    "node_id": reg_node.node_id,
                    "latitude": reg_node.latitude,
                    "longitude": reg_node.longitude,
                    "is_disease": p.is_disease,
                    "predicted_class": p.predicted_class,
                    "confidence": p.confidence,
                    "response_strength": 1.2 if p.is_disease else 0.8
                })
            else:
                all_node_prediction_inputs.append({
                    "node_id": reg_node.node_id,
                    "latitude": reg_node.latitude,
                    "longitude": reg_node.longitude,
                    "is_disease": False,
                    "predicted_class": "Healthy",
                    "confidence": 0.5,
                    "response_strength": 0.5
                })

        detected_conditions_set = set()
        for p in batch_predictions:
            if p.is_disease and p.predicted_class not in ("Rice_Healthy", "Jowar_Healthy", "Healthy"):
                detected_conditions_set.add(p.predicted_class)
        detected_conditions = sorted(list(detected_conditions_set))

        # 8. Localization & Recommendation Triggering
        localization_data: Optional[Dict[str, Any]] = None
        recommendations_data: List[Dict[str, Any]] = []

        if disease_detected_in_batch:
            farm_disease_status = "disease_detected"
            farm.status = "disease_detected"
            self.db.commit()
            localization_activated = True

            # Wind-Aware Grid-Based Source Likelihood Estimation
            localization_data = self.localization_service.estimate_source_location(
                farm_id=farm.farm_id,
                node_predictions=all_node_prediction_inputs,
                wind_speed=wind_speed,
                wind_direction=wind_dir_deg,
                farm_origin_lat=farm.latitude,
                farm_origin_lon=farm.longitude,
                save_to_db=True
            )

            # Generate farm-level disease alert with affected zone summary
            zone_summary_str = ""
            if localization_data and localization_data.get("affected_zone"):
                az = localization_data["affected_zone"]
                c_lat = az.get("center_latitude") or az.get("latitude")
                c_lon = az.get("center_longitude") or az.get("longitude")
                r_m = az.get("radius_m") or az.get("radius_meters") or 10.0
                if c_lat and c_lon:
                    zone_summary_str = f" Estimated affected zone centered near ({c_lat:.5f}, {c_lon:.5f}) with radius ~{r_m:.0f}m."

            diseased_nodes_count = sum(1 for p in batch_predictions if p.is_disease)
            avg_conf = (
                sum(p.confidence for p in batch_predictions if p.is_disease) / diseased_nodes_count
                if diseased_nodes_count > 0 else 0.8
            )
            dis_severity = "critical" if (avg_conf >= 0.85 or diseased_nodes_count >= 2) else "warning"

            farm_dis_alert = self.alert_service.create_alert(
                farm_id=farm.farm_id,
                node_id=None,
                alert_type=AlertType.DISEASE_ALERT.value,
                severity=dis_severity,
                title=f"Crop Disease Alert for Farm {farm.farm_id}: {', '.join(detected_conditions) if detected_conditions else 'Disease Detected'}",
                message=(
                    f"Bi-LSTM detection classified {', '.join(detected_conditions) if detected_conditions else 'crop disease'} "
                    f"across {diseased_nodes_count} node(s) with average confidence {avg_conf * 100:.1f}%.{zone_summary_str}"
                )
            )
            batch_alerts.append(self.alert_service._format_alert(farm_dis_alert))

            # Recommendations for all detected conditions (multi-disease support)
            recommendations_data = self.recommendation_service.generate_recommendations(
                detected_conditions=detected_conditions,
                farm_id=farm.farm_id
            )
        else:
            farm_disease_status = "healthy"
            localization_activated = False
            localization_data = {
                "active": False,
                "message": "All nodes reported healthy baseline; spatial localization inactive.",
                "farm_local": None,
                "geo": None,
                "affected_zone": None,
                "trigger_nodes": [],
                "detected_conditions": [],
                "source_score": 0.0
            }
            recommendations_data = self.recommendation_service.generate_recommendations(
                detected_conditions=[],
                farm_id=farm.farm_id
            )

        # 9. Formulate ingestion summary and response status
        if len(processed_nodes) > 0 and len(rejected_nodes) == 0:
            ingest_status = "success"
            msg = f"Successfully ingested {len(processed_nodes)} node cycles for Farm {farm.farm_id}"
        elif len(processed_nodes) > 0 and len(rejected_nodes) > 0:
            ingest_status = "partial_success"
            msg = f"Ingested {len(processed_nodes)} valid cycles; {len(rejected_nodes)} nodes rejected"
        elif len(processed_nodes) == 0 and len(rejected_nodes) > 0:
            ingest_status = "error"
            msg = f"All {len(rejected_nodes)} submitted nodes were rejected"
        else:
            ingest_status = "empty"
            msg = "No node cycles were provided in payload"

        return SensorDataIngestResponse(
            status=ingest_status,
            message=msg,
            farm_id=farm.farm_id,
            timestamp=payload.timestamp,
            processed_nodes=processed_nodes,
            rejected_nodes=rejected_nodes,
            missing_nodes=missing_nodes,
            environment_saved=env_saved,
            predictions=batch_predictions,
            farm_disease_status=farm_disease_status,
            localization_activated=localization_activated,
            localization=localization_data,
            recommendations=recommendations_data,
            alerts=batch_alerts,
            detected_conditions=detected_conditions,
            summary={
                "submitted_nodes": len(payload.nodes),
                "processed_count": len(processed_nodes),
                "rejected_count": len(rejected_nodes),
                "missing_count": len(missing_nodes),
                "predictions_count": len(batch_predictions),
                "alerts_created": len(batch_alerts)
            }
        )


    def get_node_sensor_history(
        self,
        node_id: str,
        limit: int = 50,
        only_valid: bool = False
    ) -> NodeSensorHistoryResponse:
        """
        Returns full cycle history and rolling 5-hour window readiness for a node.
        """
        node = self.node_repo.get_by_id(node_id)
        if not node:
            # Try case-insensitive
            node = self.db.query(Node).filter(func.lower(Node.node_id) == node_id.lower()).first()
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node '{node_id}' not found"
            )

        total_valid = self.sensor_cycle_repo.count_valid_cycles(node.node_id)
        prediction_ready = total_valid >= 5
        readiness_status = "ready_for_prediction" if prediction_ready else "collecting_baseline"

        latest_5 = self.sensor_cycle_repo.get_latest_valid_window(node.node_id, window_size=5)
        cycles = self.sensor_cycle_repo.get_history_for_node(node.node_id, limit=limit, only_valid=only_valid)

        return NodeSensorHistoryResponse(
            node_id=node.node_id,
            farm_id=node.farm_id,
            node_name=node.node_name,
            status=node.status,
            battery_percentage=node.battery_percentage,
            signal_strength=node.signal_strength,
            last_seen=node.last_seen,
            total_cycles=len(cycles),
            prediction_ready=prediction_ready,
            readiness_status=readiness_status,
            cycles_available=total_valid,
            cycles_required=5,
            latest_5_window=[SensorCycleItem.model_validate(c) for c in latest_5],
            cycles=[SensorCycleItem.model_validate(c) for c in cycles]
        )

    def get_farm_environment_current(self, farm_id_input: Union[int, str]) -> FarmEnvironmentCurrentResponse:
        """
        Returns latest farm microclimate (wind, ambient conditions) and current node averages.
        """
        farm = self.resolve_farm(farm_id_input)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{farm_id_input}' not found"
            )

        latest_env = self.environment_repo.get_latest_for_farm(farm.farm_id)

        # Calculate current node averages from the most recent cycle of each active node
        nodes = self.node_repo.get_by_farm_id(farm.farm_id)
        recent_temps = []
        recent_hums = []
        recent_press = []
        for n in nodes:
            c = self.sensor_cycle_repo.get_latest_cycle_for_node(n.node_id)
            if c:
                recent_temps.append(c.temperature)
                recent_hums.append(c.humidity)
                recent_press.append(c.pressure)

        node_averages = {
            "average_temperature": round(sum(recent_temps) / len(recent_temps), 2) if recent_temps else None,
            "average_humidity": round(sum(recent_hums) / len(recent_hums), 2) if recent_hums else None,
            "average_pressure": round(sum(recent_press) / len(recent_press), 2) if recent_press else None,
            "reporting_nodes": len(recent_temps)
        }

        return FarmEnvironmentCurrentResponse(
            farm_id=farm.farm_id,
            farm_name=farm.farm_name,
            latest_reading=EnvironmentReadingItem.model_validate(latest_env) if latest_env else None,
            node_averages=node_averages,
            status="operational"
        )

    def get_farm_environment_history(
        self,
        farm_id_input: Union[int, str],
        limit: int = 48
    ) -> FarmEnvironmentHistoryResponse:
        """
        Returns historical environment recordings for farm microclimate trends.
        """
        farm = self.resolve_farm(farm_id_input)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{farm_id_input}' not found"
            )

        history = self.environment_repo.get_history_for_farm(farm.farm_id, limit=limit)

        return FarmEnvironmentHistoryResponse(
            farm_id=farm.farm_id,
            count=len(history),
            history=[EnvironmentReadingItem.model_validate(r) for r in history]
        )

    def get_farm_predictions(self, farm_id_input: Union[int, str]) -> FarmPredictionsResponse:
        """
        Returns the latest predictions for all reporting nodes on a farm,
        overall farm disease status, and localization activation flag.
        """
        farm = self.resolve_farm(farm_id_input)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{farm_id_input}' not found"
            )

        latest_preds = self.prediction_repo.get_latest_by_farm(farm.farm_id)
        # Deduplicate to latest prediction per node
        node_latest: Dict[str, Any] = {}
        for p in latest_preds:
            if p.node_id not in node_latest:
                node_latest[p.node_id] = p

        results: List[NodePredictionResult] = []
        any_disease = False
        for p in node_latest.values():
            if p.disease_detected:
                any_disease = True
            results.append(NodePredictionResult(
                prediction_id=p.prediction_id,
                node_id=p.node_id,
                farm_id=p.farm_id,
                predicted_class=p.predicted_class,
                is_disease=p.disease_detected,
                confidence=p.confidence,
                probabilities=p.all_class_probabilities or p.raw_probabilities or {},
                window_start=p.window_start or p.created_at,
                window_end=p.window_end or p.created_at,
                model_version=p.model_version,
                cycle_ids=p.window_cycle_ids or []
            ))

        farm_disease_status = "disease_detected" if any_disease else "healthy"

        return FarmPredictionsResponse(
            farm_id=farm.farm_id,
            farm_name=farm.farm_name,
            farm_disease_status=farm_disease_status,
            localization_activated=any_disease,
            predictions=results
        )

    def get_node_predictions(self, node_id: str, limit: int = 50) -> List[NodePredictionResult]:
        """
        Returns prediction history for a specific hardware node.
        """
        node = self.node_repo.get_by_id(node_id)
        if not node:
            node = self.db.query(Node).filter(func.lower(Node.node_id) == node_id.lower()).first()
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node '{node_id}' not found"
            )

        preds = self.prediction_repo.get_history_by_node(node.node_id, limit=limit)
        return [
            NodePredictionResult(
                prediction_id=p.prediction_id,
                node_id=p.node_id,
                farm_id=p.farm_id,
                predicted_class=p.predicted_class,
                is_disease=p.disease_detected,
                confidence=p.confidence,
                probabilities=p.all_class_probabilities or p.raw_probabilities or {},
                window_start=p.window_start or p.created_at,
                window_end=p.window_end or p.created_at,
                model_version=p.model_version,
                cycle_ids=p.window_cycle_ids or []
            )
            for p in preds
        ]

    def get_farm_localization_latest(self, farm_id_input: Union[int, str]) -> LocalizationResponse:
        """
        Returns the latest localization estimation result for a farm.
        """
        farm = self.resolve_farm(farm_id_input)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{farm_id_input}' not found"
            )
        loc = self.localization_repo.get_latest_by_farm(farm.farm_id)
        if not loc:
            return LocalizationResponse(
                active=False,
                message="No localization event recorded for this farm yet.",
                source_score=0.0
            )
        return LocalizationResponse(
            active=loc.status == "active",
            farm_local=LocalCoordinate(x=loc.predicted_source_x or 0.0, y=loc.predicted_source_y or 0.0) if loc.predicted_source_x is not None else None,
            geo=GeoCoordinate(latitude=loc.latitude, longitude=loc.longitude),
            affected_zone=AffectedZone(
                center_x=loc.predicted_source_x or 0.0,
                center_y=loc.predicted_source_y or 0.0,
                radius_m=loc.radius_m,
                geojson=loc.affected_zone
            ),
            trigger_nodes=loc.trigger_nodes or [],
            detected_conditions=loc.detected_conditions or [],
            source_score=loc.source_score or 0.0,
            localization_id=loc.localization_id,
            timestamp=loc.timestamp,
            status=loc.status
        )

    def get_farm_localization_history(self, farm_id_input: Union[int, str], limit: int = 50) -> FarmLocalizationHistoryResponse:
        """
        Returns historical localization runs for a farm.
        """
        farm = self.resolve_farm(farm_id_input)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{farm_id_input}' not found"
            )
        history = self.localization_repo.get_history_by_farm(farm.farm_id, limit=limit)
        items = [
            LocalizationHistoryItem(
                localization_id=h.localization_id,
                farm_id=h.farm_id,
                timestamp=h.timestamp,
                predicted_source_x=h.predicted_source_x,
                predicted_source_y=h.predicted_source_y,
                latitude=h.latitude,
                longitude=h.longitude,
                radius_m=h.radius_m,
                source_score=h.source_score,
                trigger_nodes=h.trigger_nodes or [],
                detected_conditions=h.detected_conditions or [],
                affected_zone=h.affected_zone,
                severity=h.severity,
                status=h.status
            )
            for h in history
        ]
        return FarmLocalizationHistoryResponse(
            farm_id=farm.farm_id,
            total=len(items),
            history=items
        )

    def get_farm_alerts(self, farm_id_input: Union[int, str], limit: int = 50) -> FarmAlertsResponse:
        """
        Returns all alerts associated with a farm.
        """
        farm = self.resolve_farm(farm_id_input)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{farm_id_input}' not found"
            )
        alerts = self.alert_service.get_alerts_for_farm(farm.farm_id, limit=limit)
        unread = sum(1 for a in alerts if not a.get("is_read"))
        items = [
            AlertItem(
                alert_id=a["alert_id"],
                farm_id=a["farm_id"],
                node_id=a.get("node_id"),
                type=a["type"],
                alert_type=a.get("alert_type"),
                severity=a["severity"],
                title=a["title"],
                message=a["message"],
                created_at=a["created_at"],
                is_read=a["is_read"],
                is_acknowledged=a.get("is_acknowledged", False)
            )
            for a in alerts
        ]
        return FarmAlertsResponse(
            farm_id=farm.farm_id,
            total=len(items),
            unread_count=unread,
            alerts=items
        )

    def get_node_alerts(self, node_id: str, limit: int = 50) -> NodeAlertsResponse:
        """
        Returns alerts associated with a specific hardware node.
        """
        node = self.node_repo.get_by_id(node_id)
        if not node:
            node = self.db.query(Node).filter(func.lower(Node.node_id) == node_id.lower()).first()
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node '{node_id}' not found"
            )
        alerts = self.alert_service.get_alerts_for_node(node.node_id, limit=limit)
        unread = sum(1 for a in alerts if not a.get("is_read"))
        items = [
            AlertItem(
                alert_id=a["alert_id"],
                farm_id=a["farm_id"],
                node_id=a.get("node_id"),
                type=a["type"],
                alert_type=a.get("alert_type"),
                severity=a["severity"],
                title=a["title"],
                message=a["message"],
                created_at=a["created_at"],
                is_read=a["is_read"],
                is_acknowledged=a.get("is_acknowledged", False)
            )
            for a in alerts
        ]
        return NodeAlertsResponse(
            node_id=node.node_id,
            total=len(items),
            unread_count=unread,
            alerts=items
        )

    def mark_alert_read(self, alert_id: int) -> MarkAlertReadResponse:
        """
        Marks an alert as read.
        """
        alert = self.alert_service.mark_read(alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with ID {alert_id} not found"
            )
        return MarkAlertReadResponse(
            success=True,
            alert_id=alert_id,
            is_read=True,
            message=f"Alert {alert_id} marked as read"
        )

    def get_farm_recommendations(self, farm_id_input: Union[int, str], limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns generated agronomic recommendations for a farm.
        """
        farm = self.resolve_farm(farm_id_input)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm '{farm_id_input}' not found"
            )
        return self.recommendation_service.get_farm_recommendations(farm.farm_id, limit=limit)

    def check_overdue_nodes(self, farm_id_input: Optional[Union[int, str]] = None) -> List[Dict[str, Any]]:
        """
        Persistent database-driven hourly missing node monitoring.
        Checks registered nodes for expected hourly sensor cycles.
        If a node cycle is overdue (>3600 seconds or absent), creates a persistent alert.
        Prevents duplicate alert spam via AlertService deduplication.
        """
        farm_id = None
        if farm_id_input is not None:
            farm = self.resolve_farm(farm_id_input)
            if farm:
                farm_id = farm.farm_id

        if farm_id is not None:
            nodes = self.node_repo.get_by_farm_id(farm_id)
        else:
            nodes = self.db.query(Node).all()

        overdue_alerts: List[Dict[str, Any]] = []
        now = datetime.now(timezone.utc)

        for node in nodes:
            latest_cycle = self.sensor_cycle_repo.get_latest_cycle_for_node(node.node_id)
            is_overdue = False
            if not latest_cycle:
                is_overdue = True
            else:
                cycle_time = latest_cycle.cycle_timestamp
                if cycle_time.tzinfo is None:
                    cycle_time = cycle_time.replace(tzinfo=timezone.utc)
                diff_seconds = (now - cycle_time).total_seconds()
                if diff_seconds > 3600.0:
                    is_overdue = True

            if is_overdue:
                # Update node status in DB
                node.status = "offline"
                self.db.commit()

                # Create farmer alert with explicit required message text
                alert = self.alert_service.create_alert(
                    farm_id=node.farm_id,
                    node_id=node.node_id,
                    alert_type=AlertType.NODE_NO_DATA.value,
                    severity="warning",
                    title=f"Node {node.node_id} Sensor Data Overdue",
                    message=f"Node {node.node_id} has not reported sensor data for the expected hourly interval. Please check the node, power supply, connectivity, or hardware."
                )
                overdue_alerts.append(self.alert_service._format_alert(alert))

        return overdue_alerts


