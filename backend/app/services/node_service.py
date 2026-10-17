from typing import List, Optional, Any, Dict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.node import Node
from app.models.farm import Farm
from app.models.user import User, UserRole
from app.models.sensor_cycle import SensorCycle
from app.models.prediction import Prediction
from app.schemas.node import NodeCreate, NodeUpdate, NodeStatusUpdate, NodeOut
from app.schemas.node_history import NodeHistoryResponse, NodeHistoryItem
from app.schemas.prediction import PredictionItem, NodePredictionsResponse, FarmPredictionsResponse
from app.repositories.node_repo import NodeRepository
from app.repositories.farm_repo import FarmRepository
from app.repositories.farmer_repo import FarmerRepository


class NodeService:
    def __init__(self, db: Session):
        self.db = db
        self.node_repo = NodeRepository(db)
        self.farm_repo = FarmRepository(db)
        self.farmer_repo = FarmerRepository(db)

    def _verify_farm_access(self, farm_id: int, current_user: Optional[User]) -> Farm:
        farm = self.farm_repo.get_by_id(farm_id)
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {farm_id} not found"
            )
        if current_user and current_user.role == UserRole.FARMER:
            farmer = self.farmer_repo.get_by_user_id(current_user.user_id)
            if not farmer or farm.farmer_id != farmer.farmer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access nodes on this farm"
                )
        return farm

    def _enrich_node(self, node: Node) -> NodeOut:
        latest_cycle = (
            self.db.query(SensorCycle)
            .filter(SensorCycle.node_id == node.node_id)
            .order_by(desc(SensorCycle.cycle_timestamp))
            .first()
        )
        recent_cycles = (
            self.db.query(SensorCycle)
            .filter(SensorCycle.node_id == node.node_id)
            .order_by(desc(SensorCycle.cycle_timestamp))
            .limit(5)
            .all()
        )
        gas10 = latest_cycle.gas_readings if latest_cycle and latest_cycle.gas_readings else None
        temp = latest_cycle.temperature if latest_cycle else None
        hum = latest_cycle.humidity if latest_cycle else None
        press = latest_cycle.pressure if latest_cycle else None

        transmission_logs = []
        for c in recent_cycles:
            avg_gas = round(sum(c.gas_readings[:3]) / 3.0, 1) if c.gas_readings else None
            transmission_logs.append({
                "time": c.cycle_timestamp.strftime("%I:%M:%S %p"),
                "voc": f"{avg_gas} kΩ" if avg_gas is not None else "N/A",
                "temp": f"{c.temperature:.1f} °C",
                "humidity": f"{int(c.humidity)}%",
                "status": "Success (5G)"
            })

        sig_desc = "Excellent" if node.signal_strength > -70 else "Good" if node.signal_strength > -85 else "Fair"

        return NodeOut(
            node_id=node.node_id,
            farm_id=node.farm_id,
            node_name=node.node_name,
            latitude=node.latitude,
            longitude=node.longitude,
            status=node.status,
            battery_percentage=node.battery_percentage,
            signal_strength=node.signal_strength,
            firmware_version=node.firmware_version,
            is_master=node.is_master,
            last_seen=node.last_seen,
            created_at=node.created_at,
            updated_at=node.updated_at,
            battery=round(node.battery_percentage, 1) if node.battery_percentage is not None else 90.0,
            signal=sig_desc,
            signal_dbm=node.signal_strength,
            coordinates={"lat": node.latitude, "lng": node.longitude},
            hardware="ESP32 + BME688",
            power_source="Solar (with Battery)",
            device_temp=None,
            battery_voltage=5.1 if (node.battery_percentage is not None and node.battery_percentage > 50) else 4.2,
            uptime="100%",
            readings={
                "temperature": round(temp, 1) if temp is not None else None,
                "humidity": round(hum, 1) if hum is not None else None,
                "pressure": round(press, 1) if press is not None else None,
                "total_voc": round(sum(gas10[:3]) / 3.0, 1) if (gas10 and len(gas10) >= 3) else None,
                "gas_resistance_10": gas10,
                "iaq": "Good" if gas10 else "No Data"
            },
            transmission_logs=transmission_logs
        )

    def get_nodes_for_farm(self, farm_id: int, current_user: Optional[User] = None) -> List[Any]:
        self._verify_farm_access(farm_id, current_user)
        nodes = self.node_repo.get_by_farm_id(farm_id)
        return [self._enrich_node(n) for n in nodes]

    def get_node_by_id(self, node_id: str, current_user: Optional[User] = None) -> Any:
        node = self.node_repo.get_by_id(node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node with ID '{node_id}' not found"
            )
        if current_user and current_user.role == UserRole.FARMER:
            self._verify_farm_access(node.farm_id, current_user)
        return self._enrich_node(node)

    def get_raw_node_by_id(self, node_id: str, current_user: Optional[User] = None) -> Node:
        node = self.node_repo.get_by_id(node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node with ID '{node_id}' not found"
            )
        if current_user and current_user.role == UserRole.FARMER:
            self._verify_farm_access(node.farm_id, current_user)
        return node

    def create_node(self, node_in: NodeCreate, current_user: User) -> Node:
        # 1. Verify Farm exists & user has permissions
        self._verify_farm_access(node_in.farm_id, current_user)

        # 2. Check duplicate node_id
        if self.node_repo.get_by_id(node_in.node_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Node with ID '{node_in.node_id}' already exists"
            )

        # 3. Enforce maximum 3 nodes per farm constraint
        existing_count = self.node_repo.count_nodes_in_farm(node_in.farm_id)
        if existing_count >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Farm {node_in.farm_id} already has the maximum allowed capacity of 3 Bio-Sniff nodes"
            )

        return self.node_repo.create(node_in)

    def update_node(self, node_id: str, node_in: NodeUpdate, current_user: User) -> Node:
        node = self.get_raw_node_by_id(node_id, current_user=current_user)
        
        # If moving to another farm, verify destination farm capacity and access
        if node_in.farm_id is not None and node_in.farm_id != node.farm_id:
            self._verify_farm_access(node_in.farm_id, current_user)
            if self.node_repo.count_nodes_in_farm(node_in.farm_id) >= 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Target farm {node_in.farm_id} already has 3 nodes"
                )

        return self.node_repo.update(node, node_in)

    def update_node_telemetry(
        self,
        node_id: str,
        telemetry: NodeStatusUpdate
    ) -> Node:
        """Called by device ingestion pipeline or telemetry monitoring."""
        node = self.node_repo.get_by_id(node_id)
        if not node:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Node with ID '{node_id}' not found"
            )
        return self.node_repo.update_telemetry(
            node=node,
            battery_percentage=telemetry.battery_percentage,
            signal_strength=telemetry.signal_strength,
            status=telemetry.status
        )

    def delete_node(self, node_id: str, current_user: User) -> bool:
        node = self.get_raw_node_by_id(node_id, current_user=current_user)
        return self.node_repo.delete(node)

    def get_node_history(
        self,
        node_id: str,
        limit: int = 50,
        current_user: Optional[User] = None
    ) -> NodeHistoryResponse:
        node = self.get_node_by_id(node_id, current_user=current_user)
        cycles = (
            self.db.query(SensorCycle)
            .filter(SensorCycle.node_id == node_id)
            .order_by(desc(SensorCycle.cycle_timestamp))
            .limit(limit)
            .all()
        )

        history_items: List[NodeHistoryItem] = []
        for c in reversed(cycles):
            gas = c.gas_readings if isinstance(c.gas_readings, list) else []
            history_items.append(
                NodeHistoryItem(
                    cycle_id=c.cycle_id,
                    node_id=c.node_id,
                    timestamp=c.cycle_timestamp,
                    time=c.cycle_timestamp.strftime("%I %p"),
                    cycle_number=c.cycle_number,
                    temperature=c.temperature,
                    humidity=c.humidity,
                    pressure=c.pressure,
                    battery=c.battery,
                    signal=c.signal,
                    gas_readings=gas,
                    R1=gas[0] if len(gas) > 0 else None,
                    R2=gas[1] if len(gas) > 1 else None,
                    R3=gas[2] if len(gas) > 2 else None,
                    R4=gas[3] if len(gas) > 3 else None,
                    R5=gas[4] if len(gas) > 4 else None,
                    R6=gas[5] if len(gas) > 5 else None,
                    R7=gas[6] if len(gas) > 6 else None,
                    R8=gas[7] if len(gas) > 7 else None,
                    R9=gas[8] if len(gas) > 8 else None,
                    R10=gas[9] if len(gas) > 9 else None,
                )
            )

        return NodeHistoryResponse(
            node_id=node_id,
            farm_id=node.farm_id,
            count=len(history_items),
            history=history_items
        )

    def get_node_predictions(
        self,
        node_id: str,
        limit: int = 50,
        current_user: Optional[User] = None
    ) -> NodePredictionsResponse:
        node = self.get_node_by_id(node_id, current_user=current_user)
        preds = (
            self.db.query(Prediction)
            .filter(Prediction.node_id == node_id)
            .order_by(desc(Prediction.timestamp))
            .limit(limit)
            .all()
        )

        pred_items = [
            PredictionItem(
                prediction_id=p.prediction_id,
                node_id=p.node_id,
                farm_id=p.farm_id,
                cycle_id=p.cycle_id,
                timestamp=p.timestamp,
                window_start=p.window_start,
                window_end=p.window_end,
                predicted_class=p.predicted_class,
                disease_detected=p.disease_detected,
                confidence=round(p.confidence * (100.0 if p.confidence <= 1.0 else 1.0), 1) if p.confidence is not None else 0.0,
                anomaly_score=p.anomaly_score,
                all_class_probabilities=p.all_class_probabilities or p.raw_probabilities,
                model_version=p.model_version
            )
            for p in preds
        ]

        return NodePredictionsResponse(
            node_id=node_id,
            farm_id=node.farm_id,
            count=len(pred_items),
            predictions=pred_items
        )

    def get_farm_predictions(
        self,
        farm_id: int,
        limit: int = 50,
        current_user: Optional[User] = None
    ) -> FarmPredictionsResponse:
        self._verify_farm_access(farm_id, current_user)
        preds = (
            self.db.query(Prediction)
            .filter(Prediction.farm_id == farm_id)
            .order_by(desc(Prediction.timestamp))
            .limit(limit)
            .all()
        )

        pred_items = [
            PredictionItem(
                prediction_id=p.prediction_id,
                node_id=p.node_id,
                farm_id=p.farm_id,
                cycle_id=p.cycle_id,
                timestamp=p.timestamp,
                window_start=p.window_start,
                window_end=p.window_end,
                predicted_class=p.predicted_class,
                disease_detected=p.disease_detected,
                confidence=round(p.confidence * (100.0 if p.confidence <= 1.0 else 1.0), 1) if p.confidence is not None else 0.0,
                anomaly_score=p.anomaly_score,
                all_class_probabilities=p.all_class_probabilities or p.raw_probabilities,
                model_version=p.model_version
            )
            for p in preds
        ]

        diseases = [p.predicted_class for p in preds if p.disease_detected]
        farm_disease_status = ", ".join(sorted(set(diseases))) if diseases else "Healthy"
        localization_activated = len(diseases) > 0

        return FarmPredictionsResponse(
            farm_id=farm_id,
            count=len(pred_items),
            predictions=pred_items,
            farm_disease_status=farm_disease_status,
            localization_activated=localization_activated,
            detected_diseases=list(sorted(set(diseases)))
        )
