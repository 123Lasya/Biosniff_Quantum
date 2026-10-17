from typing import Optional, List, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.sensor_cycle import SensorCycle


class SensorCycleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, cycle_id: int) -> Optional[SensorCycle]:
        return self.db.query(SensorCycle).filter(SensorCycle.cycle_id == cycle_id).first()

    def is_duplicate(self, node_id: str, farm_id: int, cycle_timestamp: datetime) -> bool:
        """
        Duplicate hourly batch detection.
        Checks if a sensor cycle already exists for this (node_id, farm_id)
        with identical cycle_timestamp or within the same timestamp identity window.
        """
        existing = self.db.query(SensorCycle).filter(
            SensorCycle.node_id == node_id,
            SensorCycle.farm_id == farm_id,
            SensorCycle.cycle_timestamp == cycle_timestamp
        ).first()
        return existing is not None

    def get_next_cycle_number(self, node_id: str) -> int:
        last_cycle = self.db.query(SensorCycle).filter(
            SensorCycle.node_id == node_id
        ).order_by(SensorCycle.cycle_number.desc()).first()
        return (last_cycle.cycle_number + 1) if last_cycle else 1

    def create(
        self,
        node_id: str,
        farm_id: int,
        cycle_timestamp: datetime,
        gas_readings: List[float],
        temperature: float,
        humidity: float,
        pressure: float,
        battery: Optional[float] = None,
        signal: Optional[float] = None,
        is_valid: bool = True,
        raw_payload: Optional[Any] = None
    ) -> SensorCycle:
        cycle_number = self.get_next_cycle_number(node_id)
        cycle = SensorCycle(
            node_id=node_id,
            farm_id=farm_id,
            cycle_timestamp=cycle_timestamp,
            cycle_number=cycle_number,
            gas_readings=gas_readings,
            temperature=temperature,
            humidity=humidity,
            pressure=pressure,
            battery=battery,
            signal=signal,
            is_valid=is_valid,
            raw_payload=raw_payload,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(cycle)
        self.db.commit()
        self.db.refresh(cycle)
        return cycle

    def count_valid_cycles(self, node_id: str) -> int:
        return self.db.query(SensorCycle).filter(
            SensorCycle.node_id == node_id,
            SensorCycle.is_valid == True
        ).count()

    def get_latest_valid_window(self, node_id: str, window_size: int = 5) -> List[SensorCycle]:
        """
        Retrieves the latest valid hourly cycles for this node in chronological order [C1..Cn].
        At Hour 5: [C1, C2, C3, C4, C5]
        At Hour 6: [C2, C3, C4, C5, C6]
        """
        recent_desc = self.db.query(SensorCycle).filter(
            SensorCycle.node_id == node_id,
            SensorCycle.is_valid == True
        ).order_by(SensorCycle.cycle_timestamp.desc()).limit(window_size).all()
        # Return in ascending chronological order [C1, C2, ...]
        return list(reversed(recent_desc))

    def get_history_for_node(
        self,
        node_id: str,
        limit: int = 50,
        only_valid: bool = False
    ) -> List[SensorCycle]:
        query = self.db.query(SensorCycle).filter(SensorCycle.node_id == node_id)
        if only_valid:
            query = query.filter(SensorCycle.is_valid == True)
        return query.order_by(SensorCycle.cycle_timestamp.desc()).limit(limit).all()

    def get_latest_cycle_for_node(self, node_id: str) -> Optional[SensorCycle]:
        return self.db.query(SensorCycle).filter(
            SensorCycle.node_id == node_id
        ).order_by(SensorCycle.cycle_timestamp.desc()).first()
