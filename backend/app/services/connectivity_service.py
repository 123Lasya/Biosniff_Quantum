from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.farm import Farm
from app.models.connectivity import ConnectivityLog
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.schemas.connectivity import (
    ConnectivityCurrentResponse,
    ConnectivityHistoryItem,
    ConnectivityHistoryResponse,
)


class ConnectivityService:
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
                    detail="You do not have permission to access this farm's connectivity data"
                )
        return farm

    def get_farm_connectivity(
        self,
        farm_id: int,
        current_user: Optional[User] = None
    ) -> ConnectivityCurrentResponse:
        self._verify_farm_access(farm_id, current_user)

        log = (
            self.db.query(ConnectivityLog)
            .filter(ConnectivityLog.farm_id == farm_id)
            .order_by(desc(ConnectivityLog.recorded_at))
            .first()
        )

        if log:
            # Map RSSI to descriptive signal quality
            rssi = log.rssi
            if rssi > -70:
                signal_desc = "Excellent"
            elif rssi > -85:
                signal_desc = "Good"
            elif rssi > -100:
                signal_desc = "Fair"
            else:
                signal_desc = "Poor"

            return ConnectivityCurrentResponse(
                farm_id=farm_id,
                status=log.status.capitalize(),
                signal=signal_desc,
                signal_strength_dbm=log.rssi,
                latency=f"{int(log.latency_ms)} ms",
                latency_ms=log.latency_ms,
                upload_speed="8.4 Mbps",
                download_speed="24.6 Mbps",
                uptime="7 days (99.8%)",
                active_duration="7 days",
                packet_statistics={
                    "packets_sent_24h": "124,532",
                    "packets_received_24h": "122,870",
                    "packet_success_rate": f"{100.0 - log.packet_loss_pct:.1f}%",
                    "packet_loss_rate": f"{log.packet_loss_pct:.1f}%",
                },
                last_packet=log.recorded_at,
                network_type=f"{log.gateway_type} (NSA)",
                carrier=log.carrier,
                module_status={
                    "status": "Operational" if log.status == "connected" else "Degraded",
                    "firmware": "v2.3.1",
                    "temperature": "42°C",
                    "power_supply": "Stable (5.1 V)",
                    "errors_24h": 0 if log.packet_loss_pct < 5.0 else 2,
                }
            )

        # Response when no specific connectivity log entry is present
        return ConnectivityCurrentResponse(
            farm_id=farm_id,
            status="No Data",
            signal="No Data",
            signal_strength_dbm=0,
            latency="N/A",
            latency_ms=0.0,
            upload_speed="N/A",
            download_speed="N/A",
            uptime="N/A",
            active_duration="N/A",
            packet_statistics={
                "packets_sent_24h": "0",
                "packets_received_24h": "0",
                "packet_success_rate": "N/A",
                "packet_loss_rate": "N/A",
            },
            last_packet=datetime.now(timezone.utc),
            network_type="5G (NSA)",
            carrier="N/A",
            module_status={
                "status": "No Connectivity Data",
                "firmware": "v2.3.1",
                "temperature": "N/A",
                "power_supply": "N/A",
                "errors_24h": 0,
            }
        )

    def get_farm_connectivity_history(
        self,
        farm_id: int,
        hours: int = 24,
        limit: int = 50,
        current_user: Optional[User] = None
    ) -> ConnectivityHistoryResponse:
        self._verify_farm_access(farm_id, current_user)

        logs = (
            self.db.query(ConnectivityLog)
            .filter(ConnectivityLog.farm_id == farm_id)
            .order_by(desc(ConnectivityLog.recorded_at))
            .limit(limit)
            .all()
        )

        history_items: List[ConnectivityHistoryItem] = []
        speed_history: List[Dict[str, Any]] = []
        latency_history: List[Dict[str, Any]] = []

        if logs:
            for l in reversed(logs):
                time_str = l.recorded_at.strftime("%I %p")
                uplink = 8.4
                downlink = 24.6
                history_items.append(
                    ConnectivityHistoryItem(
                        timestamp=l.recorded_at,
                        status=l.status,
                        latency_ms=l.latency_ms,
                        uplink_mbps=uplink,
                        downlink_mbps=downlink,
                        rssi=l.rssi,
                        packet_loss_pct=l.packet_loss_pct
                    )
                )
                speed_history.append({
                    "time": time_str,
                    "uplink": uplink,
                    "downlink": downlink
                })
                latency_history.append({
                    "time": time_str,
                    "latency": int(l.latency_ms)
                })
        else:
            # Return empty history lists when no connectivity logs exist
            pass

        return ConnectivityHistoryResponse(
            farm_id=farm_id,
            count=len(history_items),
            history=history_items,
            speed_history=speed_history,
            latency_history=latency_history
        )
