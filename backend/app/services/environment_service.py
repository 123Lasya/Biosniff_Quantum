from typing import Optional, List
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.farm import Farm
from app.models.environment import EnvironmentReading
from app.models.sensor_cycle import SensorCycle
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.schemas.environment import (
    EnvironmentCurrentResponse,
    EnvironmentHistoryItem,
    EnvironmentHistoryResponse,
)


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def _verify_farm_access(self, farm_id: int, current_user: Optional[User] = None) -> Farm:
        farm = self.db.query(Farm).filter(Farm.farm_id == farm_id).first()
        if not farm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Farm with ID {farm_id} not found"
            )
        if current_user and current_user.role == UserRole.FARMER:
            farmer = self.db.query(Farmer).filter(Farmer.user_id == current_user.user_id).first()
            if not farmer or farm.farmer_id != farmer.farmer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this farm's environment data"
                )
        return farm

    def get_farm_environment(
        self,
        farm_id: int,
        current_user: Optional[User] = None
    ) -> EnvironmentCurrentResponse:
        self._verify_farm_access(farm_id, current_user)

        # 1. Check for recent microclimate EnvironmentReading
        env_reading = (
            self.db.query(EnvironmentReading)
            .filter(EnvironmentReading.farm_id == farm_id)
            .order_by(desc(EnvironmentReading.recorded_at))
            .first()
        )

        reporting_nodes_count = self.db.query(SensorCycle.node_id).filter(SensorCycle.farm_id == farm_id).distinct().count()
        nodes_count = max(reporting_nodes_count, 1)

        if env_reading:
            latest_reading = {
                "temperature": round(env_reading.ambient_temp, 1),
                "humidity": round(env_reading.humidity, 1),
                "pressure": round(env_reading.pressure, 1) if env_reading.pressure else 1008.0,
                "wind_speed": round(env_reading.wind_speed, 1),
                "wind_direction": env_reading.wind_direction or "NE (48°)",
                "soil_moisture": round(env_reading.soil_moisture, 1) if env_reading.soil_moisture else 72.0,
                "solar_radiation": env_reading.solar_radiation or 520.0,
                "recorded_at": env_reading.recorded_at.isoformat() if env_reading.recorded_at else None
            }
            node_averages = {
                "reporting_nodes": nodes_count,
                "temperature": round(env_reading.ambient_temp, 1),
                "humidity": round(env_reading.humidity, 1),
                "pressure": round(env_reading.pressure, 1) if env_reading.pressure else 1008.0
            }
            return EnvironmentCurrentResponse(
                farm_id=farm_id,
                temperature=round(env_reading.ambient_temp, 1),
                humidity=round(env_reading.humidity, 1),
                pressure=round(env_reading.pressure, 1) if env_reading.pressure else 1008.0,
                wind_speed=round(env_reading.wind_speed, 1),
                wind_direction=env_reading.wind_direction or "NE (48°)",
                wind_angle=48.0,
                soil_moisture=round(env_reading.soil_moisture, 1) if env_reading.soil_moisture else 72.0,
                solar_radiation=env_reading.solar_radiation or 520.0,
                weather_condition="Partly cloudy",
                recorded_at=env_reading.recorded_at,
                latest_reading=latest_reading,
                node_averages=node_averages
            )

        # 2. Fall back to latest sensor cycle
        latest_cycle = (
            self.db.query(SensorCycle)
            .filter(SensorCycle.farm_id == farm_id)
            .order_by(desc(SensorCycle.cycle_timestamp))
            .first()
        )

        if latest_cycle:
            latest_reading = {
                "temperature": round(latest_cycle.temperature, 1),
                "humidity": round(latest_cycle.humidity, 1),
                "pressure": round(latest_cycle.pressure, 1),
                "wind_speed": 2.4,
                "wind_direction": "NE (48°)",
                "soil_moisture": 72.0,
                "solar_radiation": 520.0,
                "recorded_at": latest_cycle.cycle_timestamp.isoformat() if latest_cycle.cycle_timestamp else None
            }
            node_averages = {
                "reporting_nodes": nodes_count,
                "temperature": round(latest_cycle.temperature, 1),
                "humidity": round(latest_cycle.humidity, 1),
                "pressure": round(latest_cycle.pressure, 1)
            }
            return EnvironmentCurrentResponse(
                farm_id=farm_id,
                temperature=round(latest_cycle.temperature, 1),
                humidity=round(latest_cycle.humidity, 1),
                pressure=round(latest_cycle.pressure, 1),
                wind_speed=2.4,
                wind_direction="NE (48°)",
                wind_angle=48.0,
                soil_moisture=72.0,
                solar_radiation=520.0,
                weather_condition="Partly cloudy",
                recorded_at=latest_cycle.cycle_timestamp,
                latest_reading=latest_reading,
                node_averages=node_averages
            )

        # 3. No environmental reading or sensor cycle present
        node_averages = {
            "reporting_nodes": 0,
            "temperature": None,
            "humidity": None,
            "pressure": None
        }
        return EnvironmentCurrentResponse(
            farm_id=farm_id,
            temperature=None,
            humidity=None,
            pressure=None,
            wind_speed=None,
            wind_direction="N/A",
            wind_angle=0.0,
            soil_moisture=None,
            solar_radiation=None,
            weather_condition="No Data",
            recorded_at=datetime.now(timezone.utc),
            latest_reading=None,
            node_averages=node_averages
        )

    def get_farm_environment_history(
        self,
        farm_id: int,
        hours: int = 24,
        limit: int = 100,
        current_user: Optional[User] = None
    ) -> EnvironmentHistoryResponse:
        self._verify_farm_access(farm_id, current_user)

        # Query EnvironmentReading records
        env_readings = (
            self.db.query(EnvironmentReading)
            .filter(EnvironmentReading.farm_id == farm_id)
            .order_by(desc(EnvironmentReading.recorded_at))
            .limit(limit)
            .all()
        )

        history_items: List[EnvironmentHistoryItem] = []

        if env_readings:
            for r in reversed(env_readings):
                history_items.append(
                    EnvironmentHistoryItem(
                        timestamp=r.recorded_at,
                        temperature=round(r.ambient_temp, 1),
                        humidity=round(r.humidity, 1),
                        pressure=round(r.pressure, 1) if r.pressure else 1008.0,
                        wind_speed=round(r.wind_speed, 1),
                        wind_direction=r.wind_direction or "NE",
                        wind_angle=48.0,
                        soil_moisture=round(r.soil_moisture, 1) if r.soil_moisture else None
                    )
                )
        else:
            # Fall back to sensor cycles
            cycles = (
                self.db.query(SensorCycle)
                .filter(SensorCycle.farm_id == farm_id)
                .order_by(desc(SensorCycle.cycle_timestamp))
                .limit(limit)
                .all()
            )
            for c in reversed(cycles):
                history_items.append(
                    EnvironmentHistoryItem(
                        timestamp=c.cycle_timestamp,
                        temperature=round(c.temperature, 1),
                        humidity=round(c.humidity, 1),
                        pressure=round(c.pressure, 1),
                        wind_speed=2.4,
                        wind_direction="NE",
                        wind_angle=48.0,
                        soil_moisture=70.0
                    )
                )

        return EnvironmentHistoryResponse(
            farm_id=farm_id,
            count=len(history_items),
            history=history_items
        )
