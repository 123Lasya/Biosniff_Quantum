from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.farms import router as farms_router
from app.api.routes.nodes import router as nodes_router
from app.api.routes.sensor_data import router as sensor_data_router

__all__ = ["health_router", "auth_router", "farms_router", "nodes_router", "sensor_data_router"]
