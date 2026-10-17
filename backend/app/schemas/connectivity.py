from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ConnectivityCurrentResponse(BaseModel):
    farm_id: int
    status: str = "Connected"
    signal: str = "Good"
    signal_strength_dbm: int = -78
    latency: str = "18 ms"
    latency_ms: float = 18.0
    upload_speed: str = "8.4 Mbps"
    download_speed: str = "24.6 Mbps"
    uptime: str = "7 days (99.8%)"
    active_duration: str = "7 days"
    packet_statistics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "packets_sent_24h": "124,532",
            "packets_received_24h": "122,870",
            "packet_success_rate": "98.7%",
            "packet_loss_rate": "1.3%",
        }
    )
    last_packet: Optional[datetime] = None
    network_type: str = "5G (NSA)"
    carrier: str = "Jio"
    module_status: Dict[str, Any] = Field(
        default_factory=lambda: {
            "status": "Operational",
            "firmware": "v2.3.1",
            "temperature": "42°C",
            "power_supply": "Stable (5.1 V)",
            "errors_24h": 0,
        }
    )

    model_config = ConfigDict(from_attributes=True)


class ConnectivityHistoryItem(BaseModel):
    timestamp: datetime
    status: str
    latency_ms: float
    uplink_mbps: float
    downlink_mbps: float
    rssi: int
    packet_loss_pct: float


class ConnectivityHistoryResponse(BaseModel):
    farm_id: int
    count: int
    history: List[ConnectivityHistoryItem] = Field(default_factory=list)
    speed_history: List[Dict[str, Any]] = Field(default_factory=list)
    latency_history: List[Dict[str, Any]] = Field(default_factory=list)
