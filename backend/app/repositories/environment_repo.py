from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.environment import EnvironmentReading


class EnvironmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        farm_id: int,
        recorded_at: datetime,
        wind_speed: float,
        wind_direction: Optional[str] = None,
        ambient_temp: float = 0.0,
        humidity: float = 0.0,
        pressure: Optional[float] = None,
        node_id: Optional[str] = None,
        soil_moisture: Optional[float] = None,
        solar_radiation: Optional[float] = None
    ) -> EnvironmentReading:
        reading = EnvironmentReading(
            farm_id=farm_id,
            node_id=node_id,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            ambient_temp=ambient_temp,
            humidity=humidity,
            pressure=pressure,
            soil_moisture=soil_moisture,
            solar_radiation=solar_radiation,
            recorded_at=recorded_at,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_latest_for_farm(self, farm_id: int) -> Optional[EnvironmentReading]:
        return self.db.query(EnvironmentReading).filter(
            EnvironmentReading.farm_id == farm_id
        ).order_by(EnvironmentReading.recorded_at.desc()).first()

    def get_history_for_farm(self, farm_id: int, limit: int = 48) -> List[EnvironmentReading]:
        return self.db.query(EnvironmentReading).filter(
            EnvironmentReading.farm_id == farm_id
        ).order_by(EnvironmentReading.recorded_at.desc()).limit(limit).all()
