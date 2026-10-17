from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.farms import router as farms_router
from app.api.routes.nodes import router as nodes_router
from app.api.routes.sensor_data import router as sensor_data_router
from app.api.routes.farmer import router as farmer_router
from app.api.routes.admin import router as admin_router
from app.api.routes.environment import router as environment_router
from app.api.routes.connectivity import router as connectivity_router
from app.api.routes.predictions import router as predictions_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(farms_router)
api_router.include_router(nodes_router)
api_router.include_router(sensor_data_router)
api_router.include_router(farmer_router)
api_router.include_router(admin_router)
api_router.include_router(environment_router)
api_router.include_router(connectivity_router)
api_router.include_router(predictions_router)

__all__ = ["api_router"]
